# Copyright 2018 Google LLC
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

"""User friendly container for Google Cloud Bigtable MutationBatcher."""


FLUSH_COUNT = 1000
MAX_MUTATIONS = 100000
MAX_ROW_BYTES = 5242880  # 5MB


class MaxMutaionsError(ValueError):
    """The number of mutations for bulk request is too big."""


class MutationsBatcher(object):
    """ A MutationsBatcher is used in batch cases where the number of mutations
    is large or unknown. It will store DirectRows in memory until one of the
    size limits is reached, or an explicit call to flush() is performed. When
    a flush event occurs, the DirectRows in memory will be sent to Cloud
    Bigtable. Batching mutations is more efficient than sending individual
    request.

    This class is not suited for usage in systems where each mutation
    needs to guaranteed to be sent, since calling mutate may only result in an
    in-memory change. In a case of a system crash, any DirectRows remaining in
    memory will not necessarily be sent to the service, even after the
    completion of the mutate() method.

    TODO: Performance would dramatically improve if this class had the
    capability of asynchronous, parallel RPCs.

    :type table: class
    :param table: class:`~google.cloud.bigtable.table.Table`.

    :type flush_count: int
    :param flush_count: (Optional) Max number of rows to flush. If it
    reaches the max number of rows it calls finish_batch() to mutate the
    current row batch. Default is FLUSH_COUNT (1000 rows).

    :type max_row_bytes: int
    :param max_row_bytes: (Optional) Max number of row mutations size to
    flush. If it reaches the max number of row mutations size it calls
    finish_batch() to mutate the current row batch. Default is MAX_ROW_BYTES
    (5 MB).
    """

    def __init__(self, table, flush_count=FLUSH_COUNT,
                 max_row_bytes=MAX_ROW_BYTES):
        self.rows = []
        self.total_mutation_count = 0
        self.total_size = 0
        self.table = table
        self.flush_count = flush_count
        self.max_row_bytes = max_row_bytes

    def mutate(self, row):
        """ Add a row to the batch. If the current batch meets one of the size
        limits, the batch is sent synchronously.

        Example:
            >>> # Batcher for flush count
            >>> batcher = table.batcher(flush_count=10)
            >>>
            >>> rows = ["list of 1000 rows"]
            >>>
            >>> # In batcher mutate will create batch of 10 rows if it
            >>> # reaches the max flush_count
            >>> for row in rows:
            >>>     batcher.mutate(row)
            >>>
            >>> batcher.flush()
            >>>
            >>> # Batcher for max row bytes
            >>> batcher = table.batcher(max_row_bytes=1024)
            >>>
            >>> rows = ["list of 1000 rows"]
            >>>
            >>> # In batcher mutate will create batch of rows if it
            >>> # reaches the max max_row_bytes
            >>> for row in rows:
            >>>     batcher.mutate(row)
            >>>
            >>> batcher.flush()

        :type row: class
        :param row: class:`~google.cloud.bigtable.row.DirectRow`.

        :raises: One of the following:
                 * :exc:`~.table._BigtableRetryableError` if any
                   row returned a transient error.
                 * :exc:`RuntimeError` if the number of responses doesn't
                   match the number of rows that were retried
                 * :exc:`.batcher.MaxMutaionsError` if any row exceeds max
                   mutaions count.
        """
        mutation_count = len(row._get_mutations())
        if mutation_count > MAX_MUTATIONS:
            raise MaxMutaionsError(
                'The row key {} exceeds the number of mutations {}.'.format(
                    row.row_key, mutation_count), )

        if (self.total_mutation_count + mutation_count) >= MAX_MUTATIONS:
            self.flush()

        self.rows.append(row)
        self.total_mutation_count += mutation_count
        self.total_size += row.get_mutations_size()

        if (self.total_size >= self.max_row_bytes or
                len(self.rows) >= self.flush_count):
            self.flush()

    def flush(self):
        """ Sends the current. batch to Cloud Bigtable. """
        if len(self.rows) is not 0:
            self.table.mutate_rows(self.rows)
            self.total_mutation_count = 0
            self.total_size = 0
            self.rows = []
