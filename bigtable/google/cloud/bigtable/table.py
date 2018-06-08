# Copyright 2015 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""User-friendly container for Google Cloud Bigtable Table."""


from grpc import StatusCode

from google.api_core.exceptions import RetryError
from google.api_core.retry import if_exception_type
from google.api_core.retry import Retry
from google.cloud._helpers import _to_bytes
from google.cloud.bigtable_v2.proto import (
    bigtable_pb2 as data_messages_v2_pb2)
from google.cloud.bigtable.column_family import _gc_rule_from_pb
from google.cloud.bigtable.column_family import ColumnFamily
from google.cloud.bigtable.row import AppendRow
from google.cloud.bigtable.row import ConditionalRow
from google.cloud.bigtable.row import DirectRow
from google.cloud.bigtable.row_data import PartialRowsData
from google.cloud.bigtable.row_data import YieldRowsData


# Maximum number of mutations in bulk (MutateRowsRequest message):
# (https://cloud.google.com/bigtable/docs/reference/data/rpc/
#  google.bigtable.v2#google.bigtable.v2.MutateRowRequest)
_MAX_BULK_MUTATIONS = 100000


class _BigtableRetryableError(Exception):
    """Retry-able error expected by the default retry strategy."""


DEFAULT_RETRY = Retry(
    predicate=if_exception_type(_BigtableRetryableError),
    initial=1.0,
    maximum=15.0,
    multiplier=2.0,
    deadline=120.0,  # 2 minutes
)
"""The default retry stategy to be used on retry-able errors.

Used by :meth:`~google.cloud.bigtable.table.Table.mutate_rows`.
"""


class TableMismatchError(ValueError):
    """Row from another table."""


class TooManyMutationsError(ValueError):
    """The number of mutations for bulk request is too big."""


class Table(object):
    """Representation of a Google Cloud Bigtable Table.

    .. note::

        We don't define any properties on a table other than the name.
        The only other fields are ``column_families`` and ``granularity``,
        The ``column_families`` are not stored locally and
        ``granularity`` is an enum with only one value.

    We can use a :class:`Table` to:

    * :meth:`create` the table
    * :meth:`delete` the table
    * :meth:`list_column_families` in the table

    :type table_id: str
    :param table_id: The ID of the table.

    :type instance: :class:`~google.cloud.bigtable.instance.Instance`
    :param instance: The instance that owns the table.

    :type: app_profile_id: str
    :param app_profile_id: (Optional) The unique name of the AppProfile.
    """

    def __init__(self, table_id, instance, app_profile_id=None):
        self.table_id = table_id
        self._instance = instance
        self._app_profile_id = app_profile_id

    @property
    def name(self):
        """Table name used in requests.

        .. note::

          This property will not change if ``table_id`` does not, but the
          return value is not cached.

        The table name is of the form

            ``"projects/../instances/../tables/{table_id}"``

        :rtype: str
        :returns: The table name.
        """
        project = self._instance._client.project
        instance_id = self._instance.instance_id
        table_client = self._instance._client.table_admin_client
        return table_client.table_path(
            project=project, instance=instance_id, table=self.table_id)

    def column_family(self, column_family_id, gc_rule=None):
        """Factory to create a column family associated with this table.

        :type column_family_id: str
        :param column_family_id: The ID of the column family. Must be of the
                                 form ``[_a-zA-Z0-9][-_.a-zA-Z0-9]*``.

        :type gc_rule: :class:`.GarbageCollectionRule`
        :param gc_rule: (Optional) The garbage collection settings for this
                        column family.

        :rtype: :class:`.ColumnFamily`
        :returns: A column family owned by this table.
        """
        return ColumnFamily(column_family_id, self, gc_rule=gc_rule)

    def row(self, row_key, filter_=None, append=False):
        """Factory to create a row associated with this table.

        .. warning::

           At most one of ``filter_`` and ``append`` can be used in a
           :class:`~google.cloud.bigtable.row.Row`.

        :type row_key: bytes
        :param row_key: The key for the row being created.

        :type filter_: :class:`.RowFilter`
        :param filter_: (Optional) Filter to be used for conditional mutations.
                        See :class:`.ConditionalRow` for more details.

        :type append: bool
        :param append: (Optional) Flag to determine if the row should be used
                       for append mutations.

        :rtype: :class:`~google.cloud.bigtable.row.Row`
        :returns: A row owned by this table.
        :raises: :class:`ValueError <exceptions.ValueError>` if both
                 ``filter_`` and ``append`` are used.
        """
        if append and filter_ is not None:
            raise ValueError('At most one of filter_ and append can be set')
        if append:
            return AppendRow(row_key, self)
        elif filter_ is not None:
            return ConditionalRow(row_key, self, filter_=filter_)
        else:
            return DirectRow(row_key, self)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (other.table_id == self.table_id and
                other._instance == self._instance)

    def __ne__(self, other):
        return not self == other

    def create(self):
        """Creates this table.

        .. note::

            A create request returns a
            :class:`._generated.table_pb2.Table` but we don't use
            this response.
        """
        table_client = self._instance._client.table_admin_client
        instance_name = self._instance.name
        table_client.create_table(
            parent=instance_name, table_id=self.table_id, table={})

    def delete(self):
        """Delete this table."""
        table_client = self._instance._client.table_admin_client
        table_client.delete_table(name=self.name)

    def list_column_families(self):
        """List the column families owned by this table.

        :rtype: dict
        :returns: Dictionary of column families attached to this table. Keys
                  are strings (column family names) and values are
                  :class:`.ColumnFamily` instances.
        :raises: :class:`ValueError <exceptions.ValueError>` if the column
                 family name from the response does not agree with the computed
                 name from the column family ID.
        """
        table_client = self._instance._client.table_admin_client
        table_pb = table_client.get_table(self.name)

        result = {}
        for column_family_id, value_pb in table_pb.column_families.items():
            gc_rule = _gc_rule_from_pb(value_pb.gc_rule)
            column_family = self.column_family(column_family_id,
                                               gc_rule=gc_rule)
            result[column_family_id] = column_family
        return result

    def read_row(self, row_key, filter_=None):
        """Read a single row from this table.

        :type row_key: bytes
        :param row_key: The key of the row to read from.

        :type filter_: :class:`.RowFilter`
        :param filter_: (Optional) The filter to apply to the contents of the
                        row. If unset, returns the entire row.

        :rtype: :class:`.PartialRowData`, :data:`NoneType <types.NoneType>`
        :returns: The contents of the row if any chunks were returned in
                  the response, otherwise :data:`None`.
        :raises: :class:`ValueError <exceptions.ValueError>` if a commit row
                 chunk is never encountered.
        """
        request_pb = _create_row_request(
            self.name, row_key=row_key, filter_=filter_,
            app_profile_id=self._app_profile_id)
        data_client = self._instance._client.table_data_client
        rows_data = PartialRowsData(data_client._read_rows, request_pb)

        rows_data.consume_all()
        if rows_data.state not in (rows_data.NEW_ROW, rows_data.START):
            raise ValueError('The row remains partial / is not committed.')

        if len(rows_data.rows) == 0:
            return None

        return rows_data.rows[row_key]

    def read_rows(self, start_key=None, end_key=None, limit=None,
                  filter_=None, end_inclusive=False):
        """Read rows from this table.

        :type start_key: bytes
        :param start_key: (Optional) The beginning of a range of row keys to
                          read from. The range will include ``start_key``. If
                          left empty, will be interpreted as the empty string.

        :type end_key: bytes
        :param end_key: (Optional) The end of a range of row keys to read from.
                        The range will not include ``end_key``. If left empty,
                        will be interpreted as an infinite string.

        :type limit: int
        :param limit: (Optional) The read will terminate after committing to N
                      rows' worth of results. The default (zero) is to return
                      all results.

        :type filter_: :class:`.RowFilter`
        :param filter_: (Optional) The filter to apply to the contents of the
                        specified row(s). If unset, reads every column in
                        each row.

        :type end_inclusive: bool
        :param end_inclusive: (Optional) Whether the ``end_key`` should be
                      considered inclusive. The default is False (exclusive).

        :rtype: :class:`.PartialRowsData`
        :returns: A :class:`.PartialRowsData` convenience wrapper for consuming
                  the streamed results.
        """
        request_pb = _create_row_request(
            self.name, start_key=start_key, end_key=end_key,
            filter_=filter_, limit=limit, end_inclusive=end_inclusive,
            app_profile_id=self._app_profile_id)
        data_client = self._instance._client.table_data_client
        return PartialRowsData(data_client._read_rows, request_pb)

    def yield_rows(self, start_key=None, end_key=None, limit=None,
                   filter_=None):
        """Read rows from this table.

        :type start_key: bytes
        :param start_key: (Optional) The beginning of a range of row keys to
                          read from. The range will include ``start_key``. If
                          left empty, will be interpreted as the empty string.

        :type end_key: bytes
        :param end_key: (Optional) The end of a range of row keys to read from.
                        The range will not include ``end_key``. If left empty,
                        will be interpreted as an infinite string.

        :type limit: int
        :param limit: (Optional) The read will terminate after committing to N
                      rows' worth of results. The default (zero) is to return
                      all results.

        :type filter_: :class:`.RowFilter`
        :param filter_: (Optional) The filter to apply to the contents of the
                        specified row(s). If unset, reads every column in
                        each row.

        :rtype: :class:`.PartialRowData`
        :returns: A :class:`.PartialRowData` for each row returned
        """
        request_pb = _create_row_request(
            self.name, start_key=start_key, end_key=end_key, filter_=filter_,
            limit=limit, app_profile_id=self._app_profile_id)
        data_client = self._instance._client.table_data_client
        generator = YieldRowsData(data_client._read_rows, request_pb)

        for row in generator.read_rows():
            yield row

    def save_mutations(self, row_mutations, retry=DEFAULT_RETRY):
        """ Save row mutations

        :type row_mutations: list: [`RowMutations`]
        :param row_mutations: The list of RowMutations to save

        :type retry: class:`~google.api_core.retry.Retry`
        :param retry: (Optional) Retry delay and deadline arguments. To
                        override, the default value :attr:`DEFAULT_RETRY` can
                        be used and modified with the
                        :meth:`~google.api_core.retry.Retry.with_delay` method
                        or the
                        :meth:`~google.api_core.retry.Retry.with_deadline`
                        method.

        :rtype: list: [`~google.rpc.status_pb2.Status`]
        :return: The response statuses, which is a list of
                 :class:`~google.rpc.status_pb2.Status`.
        """
        retryable_mutate_rows_status = _RetryableMutateRowsWorker(
            self._instance._client, self.name, row_mutations)
        return retryable_mutate_rows_status(retry=retry)

    def mutate_rows(self, rows, retry=DEFAULT_RETRY):
        """Mutates multiple rows in bulk.

        The method tries to update all specified rows.
        If some of the rows weren't updated, it would not remove mutations.
        They can be applied to the row separately.
        If row mutations finished successfully, they would be cleaned up.

        Optionally, a ``retry`` strategy can be specified to re-attempt
        mutations on rows that return transient errors. This method will retry
        until all rows succeed or until the request deadline is reached. To
        specify a ``retry`` strategy of "do-nothing", a deadline of ``0.0``
        can be specified.

        :type rows: list
        :param rows: List or other iterable of :class:`.DirectRow` instances.

        :type retry: class:`~google.api_core.retry.Retry`
        :param retry: (Optional) Retry delay and deadline arguments. To
                        override, the default value :attr:`DEFAULT_RETRY` can
                        be used and modified with the
                        :meth:`~google.api_core.retry.Retry.with_delay` method
                        or the
                        :meth:`~google.api_core.retry.Retry.with_deadline`
                        method.

        :rtype: list
        :returns: A list of response statuses (`google.rpc.status_pb2.Status`)
                  corresponding to success or failure of each row mutation
                  sent. These will be in the same order as the `rows`.
        """
        mutation_rows = map(lambda row: row.row_mutations, rows)
        for row in rows:
            mutation_rows.append(row.row_mutations)

        return self.save_mutations(mutation_rows, retry)

    def sample_row_keys(self):
        """Read a sample of row keys in the table.

        The returned row keys will delimit contiguous sections of the table of
        approximately equal size, which can be used to break up the data for
        distributed tasks like mapreduces.

        The elements in the iterator are a SampleRowKeys response and they have
        the properties ``offset_bytes`` and ``row_key``. They occur in sorted
        order. The table might have contents before the first row key in the
        list and after the last one, but a key containing the empty string
        indicates "end of table" and will be the last response given, if
        present.

        .. note::

            Row keys in this list may not have ever been written to or read
            from, and users should therefore not make any assumptions about the
            row key structure that are specific to their use case.

        The ``offset_bytes`` field on a response indicates the approximate
        total storage space used by all rows in the table which precede
        ``row_key``. Buffering the contents of all rows between two subsequent
        samples would require space roughly equal to the difference in their
        ``offset_bytes`` fields.

        :rtype: :class:`~google.cloud.exceptions.GrpcRendezvous`
        :returns: A cancel-able iterator. Can be consumed by calling ``next()``
                  or by casting to a :class:`list` and can be cancelled by
                  calling ``cancel()``.
        """
        data_client = self._instance._client.table_data_client
        response_iterator = data_client.sample_row_keys(
            self.name, app_profile_id=self._app_profile_id)

        return response_iterator


class _RetryableMutateRowsWorker(object):
    """A callable worker that can retry to mutate rows with transient errors.

    This class is a callable that can retry mutating rows that result in
    transient errors. After all rows are successful or none of the rows
    are retryable, any subsequent call on this callable will be a no-op.
    """

    # pylint: disable=unsubscriptable-object
    RETRY_CODES = (
        StatusCode.DEADLINE_EXCEEDED.value[0],
        StatusCode.ABORTED.value[0],
        StatusCode.UNAVAILABLE.value[0],
    )
    # pylint: enable=unsubscriptable-object

    def __init__(self, client, table_name, rows, app_profile_id=None):
        self.client = client
        self.table_name = table_name
        self.rows = rows
        self.app_profile_id = app_profile_id
        self.responses_statuses = [None] * len(self.rows)

    def __call__(self, retry=DEFAULT_RETRY):
        """Attempt to mutate all rows and retry rows with transient errors.

        Will retry the rows with transient errors until all rows succeed or
        ``deadline`` specified in the `retry` is reached.

        :rtype: list
        :returns: A list of response statuses (`google.rpc.status_pb2.Status`)
                  corresponding to success or failure of each row mutation
                  sent. These will be in the same order as the ``rows``.
        """
        mutate_rows = self._do_mutate_retryable_rows
        if retry:
            mutate_rows = retry(self._do_mutate_retryable_rows)

        try:
            mutate_rows()
        except (_BigtableRetryableError, RetryError) as err:
            # - _BigtableRetryableError raised when no retry strategy is used
            #   and a retryable error on a mutation occurred.
            # - RetryError raised when retry deadline is reached.
            # In both cases, just return current `responses_statuses`.
            pass

        return self.responses_statuses

    @staticmethod
    def _is_retryable(status):
        return (status is None or
                status.code in _RetryableMutateRowsWorker.RETRY_CODES)

    def _mutate_rows_entries(self, mutation_rows):
        entries = []
        mutations_count = 0
        for mutation_row in mutation_rows:
            mutations_count += 1
            entries.append(mutation_row.create_entry())

        if mutations_count > _MAX_BULK_MUTATIONS:
            raise TooManyMutationsError('Maximum number of mutations is %s' %
                                        (_MAX_BULK_MUTATIONS,))

        return entries

    def _do_mutate_retryable_rows(self):
        """Mutate all the rows that are eligible for retry.

        A row is eligible for retry if it has not been tried or if it resulted
        in a transient error in a previous call.

        :rtype: list
        :return: The responses statuses, which is a list of
                 :class:`~google.rpc.status_pb2.Status`.
        :raises: One of the following:

                 * :exc:`~.table._BigtableRetryableError` if any
                   row returned a transient error.
                 * :exc:`RuntimeError` if the number of responses doesn't
                   match the number of rows that were retried
        """
        retryable_rows = []
        index_into_all_rows = []
        for index, status in enumerate(self.responses_statuses):
            if self._is_retryable(status):
                retryable_rows.append(self.rows[index])
                index_into_all_rows.append(index)

        if not retryable_rows:
            # All mutations are either successful or non-retryable now.
            return self.responses_statuses

        mutate_rows_entries = self._mutate_rows_entries(retryable_rows)
        responses = self.client._table_data_client.mutate_rows(
            table_name=self.table_name,
            entries=mutate_rows_entries,
            app_profile_id=self.app_profile_id
        )

        num_responses = 0
        num_retryable_responses = 0
        for response in responses:
            for entry in response.entries:
                num_responses += 1
                index = index_into_all_rows[entry.index]
                self.responses_statuses[index] = entry.status
                if self._is_retryable(entry.status):
                    num_retryable_responses += 1
                if entry.status.code == 0:
                    self.rows[index] = None

        if len(retryable_rows) != num_responses:
            raise RuntimeError(
                'Unexpected number of responses', num_responses,
                'Expected', len(retryable_rows))

        if num_retryable_responses:
            raise _BigtableRetryableError

        self.rows = []
        return self.responses_statuses


def _create_row_request(table_name, row_key=None, start_key=None, end_key=None,
                        filter_=None, limit=None, end_inclusive=False,
                        app_profile_id=None):
    """Creates a request to read rows in a table.

    :type table_name: str
    :param table_name: The name of the table to read from.

    :type row_key: bytes
    :param row_key: (Optional) The key of a specific row to read from.

    :type start_key: bytes
    :param start_key: (Optional) The beginning of a range of row keys to
                      read from. The range will include ``start_key``. If
                      left empty, will be interpreted as the empty string.

    :type end_key: bytes
    :param end_key: (Optional) The end of a range of row keys to read from.
                    The range will not include ``end_key``. If left empty,
                    will be interpreted as an infinite string.

    :type filter_: :class:`.RowFilter`
    :param filter_: (Optional) The filter to apply to the contents of the
                    specified row(s). If unset, reads the entire table.

    :type limit: int
    :param limit: (Optional) The read will terminate after committing to N
                  rows' worth of results. The default (zero) is to return
                  all results.

    :type end_inclusive: bool
    :param end_inclusive: (Optional) Whether the ``end_key`` should be
                  considered inclusive. The default is False (exclusive).

    :type: app_profile_id: str
    :param app_profile_id: (Optional) The unique name of the AppProfile.

    :rtype: :class:`data_messages_v2_pb2.ReadRowsRequest`
    :returns: The ``ReadRowsRequest`` protobuf corresponding to the inputs.
    :raises: :class:`ValueError <exceptions.ValueError>` if both
             ``row_key`` and one of ``start_key`` and ``end_key`` are set
    """
    request_kwargs = {'table_name': table_name}
    if (row_key is not None and
            (start_key is not None or end_key is not None)):
        raise ValueError('Row key and row range cannot be '
                         'set simultaneously')
    range_kwargs = {}
    if start_key is not None or end_key is not None:
        if start_key is not None:
            range_kwargs['start_key_closed'] = _to_bytes(start_key)
        if end_key is not None:
            end_key_key = 'end_key_open'
            if end_inclusive:
                end_key_key = 'end_key_closed'
            range_kwargs[end_key_key] = _to_bytes(end_key)
    if filter_ is not None:
        request_kwargs['filter'] = filter_.to_pb()
    if limit is not None:
        request_kwargs['rows_limit'] = limit
    if app_profile_id is not None:
        request_kwargs['app_profile_id'] = app_profile_id

    message = data_messages_v2_pb2.ReadRowsRequest(**request_kwargs)

    if row_key is not None:
        message.rows.row_keys.append(_to_bytes(row_key))

    if range_kwargs:
        message.rows.row_ranges.add(**range_kwargs)

    return message


def _mutate_rows_request(table_name, rows, app_profile_id=None):
    """Creates a request to mutate rows in a table.

    :type table_name: str
    :param table_name: The name of the table to write to.

    :type rows: list
    :param rows: List or other iterable of :class:`.DirectRow` instances.

    :type: app_profile_id: str
    :param app_profile_id: (Optional) The unique name of the AppProfile.

    :rtype: :class:`data_messages_v2_pb2.MutateRowsRequest`
    :returns: The ``MutateRowsRequest`` protobuf corresponding to the inputs.
    :raises: :exc:`~.table.TooManyMutationsError` if the number of mutations is
             greater than 100,000
    """
    request_pb = data_messages_v2_pb2.MutateRowsRequest(
        table_name=table_name, app_profile_id=app_profile_id)
    mutations_count = 0
    for row in rows:
        _check_row_table_name(table_name, row)
        _check_row_type(row)
        entry = request_pb.entries.add()
        entry.row_key = row.row_key
        # NOTE: Since `_check_row_type` has verified `row` is a `DirectRow`,
        #  the mutations have no state.
        for mutation in row.row_mutations.mutations:
            mutations_count += 1
            entry.mutations.add().CopyFrom(mutation)
    if mutations_count > _MAX_BULK_MUTATIONS:
        raise TooManyMutationsError('Maximum number of mutations is %s' %
                                    (_MAX_BULK_MUTATIONS,))
    return request_pb


def _check_row_table_name(table_name, row):
    """Checks that a row belongs to a table.

    :type table_name: str
    :param table_name: The name of the table.

    :type row: :class:`~google.cloud.bigtable.row.Row`
    :param row: An instance of :class:`~google.cloud.bigtable.row.Row`
                subclasses.

    :raises: :exc:`~.table.TableMismatchError` if the row does not belong to
             the table.
    """
    if row.table.name != table_name:
        raise TableMismatchError(
            'Row %s is a part of %s table. Current table: %s' %
            (row.row_key, row.table.name, table_name))


def _check_row_type(row):
    """Checks that a row is an instance of :class:`.DirectRow`.

    :type row: :class:`~google.cloud.bigtable.row.Row`
    :param row: An instance of :class:`~google.cloud.bigtable.row.Row`
                subclasses.

    :raises: :class:`TypeError <exceptions.TypeError>` if the row is not an
             instance of DirectRow.
    """
    if not isinstance(row, DirectRow):
        raise TypeError('Bulk processing can not be applied for '
                        'conditional or append mutations.')
