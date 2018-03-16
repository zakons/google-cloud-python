# Copyright 2016 Google LLC
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


import unittest

import mock


class TestCell(unittest.TestCase):
    timestamp_micros = 18738724000  # Make sure millis granularity

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.row_data import Cell

        return Cell

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _from_pb_test_helper(self, labels=None):
        import datetime
        from google.cloud._helpers import _EPOCH
        from google.cloud.bigtable._generated import (
            data_pb2 as data_v2_pb2)

        timestamp_micros = TestCell.timestamp_micros
        timestamp = _EPOCH + datetime.timedelta(microseconds=timestamp_micros)
        value = b'value-bytes'

        if labels is None:
            cell_pb = data_v2_pb2.Cell(
                value=value, timestamp_micros=timestamp_micros)
            cell_expected = self._make_one(value, timestamp_micros)
        else:
            cell_pb = data_v2_pb2.Cell(
                value=value, timestamp_micros=timestamp_micros, labels=labels)
            cell_expected = self._make_one(
                value, timestamp_micros, labels=labels)

        klass = self._get_target_class()
        result = klass.from_pb(cell_pb)
        self.assertEqual(result, cell_expected)
        self.assertEqual(result.timestamp, timestamp)

    def test_from_pb(self):
        self._from_pb_test_helper()

    def test_from_pb_with_labels(self):
        labels = [u'label1', u'label2']
        self._from_pb_test_helper(labels)

    def test_constructor(self):
        value = object()
        cell = self._make_one(value, TestCell.timestamp_micros)
        self.assertEqual(cell.value, value)

    def test___eq__(self):
        value = object()
        cell1 = self._make_one(value, TestCell.timestamp_micros)
        cell2 = self._make_one(value, TestCell.timestamp_micros)
        self.assertEqual(cell1, cell2)

    def test___eq__type_differ(self):
        cell1 = self._make_one(None, None)
        cell2 = object()
        self.assertNotEqual(cell1, cell2)

    def test___ne__same_value(self):
        value = object()
        cell1 = self._make_one(value, TestCell.timestamp_micros)
        cell2 = self._make_one(value, TestCell.timestamp_micros)
        comparison_val = (cell1 != cell2)
        self.assertFalse(comparison_val)

    def test___ne__(self):
        value1 = 'value1'
        value2 = 'value2'
        cell1 = self._make_one(value1, TestCell.timestamp_micros)
        cell2 = self._make_one(value2, TestCell.timestamp_micros)
        self.assertNotEqual(cell1, cell2)


class TestPartialRowData(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.row_data import PartialRowData

        return PartialRowData

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_constructor(self):
        row_key = object()
        partial_row_data = self._make_one(row_key)
        self.assertIs(partial_row_data._row_key, row_key)
        self.assertEqual(partial_row_data._cells, {})

    def test___eq__(self):
        row_key = object()
        partial_row_data1 = self._make_one(row_key)
        partial_row_data2 = self._make_one(row_key)
        self.assertEqual(partial_row_data1, partial_row_data2)

    def test___eq__type_differ(self):
        partial_row_data1 = self._make_one(None)
        partial_row_data2 = object()
        self.assertNotEqual(partial_row_data1, partial_row_data2)

    def test___ne__same_value(self):
        row_key = object()
        partial_row_data1 = self._make_one(row_key)
        partial_row_data2 = self._make_one(row_key)
        comparison_val = (partial_row_data1 != partial_row_data2)
        self.assertFalse(comparison_val)

    def test___ne__(self):
        row_key1 = object()
        partial_row_data1 = self._make_one(row_key1)
        row_key2 = object()
        partial_row_data2 = self._make_one(row_key2)
        self.assertNotEqual(partial_row_data1, partial_row_data2)

    def test___ne__cells(self):
        row_key = object()
        partial_row_data1 = self._make_one(row_key)
        partial_row_data1._cells = object()
        partial_row_data2 = self._make_one(row_key)
        self.assertNotEqual(partial_row_data1, partial_row_data2)

    def test_to_dict(self):
        cell1 = object()
        cell2 = object()
        cell3 = object()

        family_name1 = u'name1'
        family_name2 = u'name2'
        qual1 = b'col1'
        qual2 = b'col2'
        qual3 = b'col3'

        partial_row_data = self._make_one(None)
        partial_row_data._cells = {
            family_name1: {
                qual1: cell1,
                qual2: cell2,
            },
            family_name2: {
                qual3: cell3,
            },
        }

        result = partial_row_data.to_dict()
        expected_result = {
            b'name1:col1': cell1,
            b'name1:col2': cell2,
            b'name2:col3': cell3,
        }
        self.assertEqual(result, expected_result)

    def test_cells_property(self):
        partial_row_data = self._make_one(None)
        cells = {1: 2}
        partial_row_data._cells = cells
        # Make sure we get a copy, not the original.
        self.assertIsNot(partial_row_data.cells, cells)
        self.assertEqual(partial_row_data.cells, cells)

    def test_row_key_getter(self):
        row_key = object()
        partial_row_data = self._make_one(row_key)
        self.assertIs(partial_row_data.row_key, row_key)


class _Client(object):

    data_stub = None


class TestPartialRowsData(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.row_data import PartialRowsData

        return PartialRowsData

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_constructor(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        partial_rows_data = self._make_one(client._data_stub.ReadRows,
                                           request)
        self.assertIs(partial_rows_data._generator.request,
                      request)
        self.assertEqual(partial_rows_data.rows, {})

    def test___eq__(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        partial_rows_data1 = self._make_one(client._data_stub.ReadRows,
                                            request)
        partial_rows_data2 = self._make_one(client._data_stub.ReadRows,
                                            request)
        self.assertEqual(partial_rows_data1.rows, partial_rows_data2.rows)

    def test___eq__type_differ(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        partial_rows_data1 = self._make_one(client._data_stub.ReadRows,
                                            request)
        partial_rows_data2 = object()
        self.assertNotEqual(partial_rows_data1, partial_rows_data2)

    def test___ne__same_value(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        partial_rows_data1 = self._make_one(client._data_stub.ReadRows,
                                            request)
        partial_rows_data2 = self._make_one(client._data_stub.ReadRows,
                                            request)
        comparison_val = (partial_rows_data1 != partial_rows_data2)
        self.assertTrue(comparison_val)

    def test___ne__(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        partial_rows_data1 = self._make_one(client._data_stub.ReadRows,
                                            request)
        partial_rows_data2 = self._make_one(client._data_stub.ReadRows,
                                            request)
        self.assertNotEqual(partial_rows_data1, partial_rows_data2)

    def test_rows_getter(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        partial_rows_data = self._make_one(client._data_stub.ReadRows,
                                           request)
        partial_rows_data.rows = value = object()
        self.assertIs(partial_rows_data.rows, value)


class TestYieldRowsData(unittest.TestCase):
    ROW_KEY = b'row-key'
    FAMILY_NAME = u'family'
    QUALIFIER = b'qualifier'
    TIMESTAMP_MICROS = 100
    VALUE = b'value'

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.row_data import YieldRowsData

        return YieldRowsData

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_state_start(self):
        client = _Client()
        iterator = _MockCancellableIterator()
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        self.assertEqual(yrd.state, yrd.START)

    def test_state_new_row_w_row(self):
        client = _Client()
        iterator = _MockCancellableIterator()
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        yrd.last_scanned_row_key = ''
        yrd._row = object()
        self.assertEqual(yrd.state, yrd.NEW_ROW)

    def test_cancel(self):
        client = _Client()
        response_iterator = _MockCancellableIterator()
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [response_iterator]
        request = object()
        yield_rows_data = self._make_one(client._data_stub.ReadRows, request)
        self.assertEqual(response_iterator.cancel_calls, 0)
        yield_rows_data.cancel()
        self.assertEqual(response_iterator.cancel_calls, 1)

    # 'consume_next' tested via 'TestPartialRowsData_JSON_acceptance_tests'

    def test__copy_from_current_unset(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        chunks = _generate_cell_chunks([''])
        chunk = chunks[0]
        yrd._copy_from_current(chunk)
        self.assertEqual(chunk.row_key, b'')
        self.assertEqual(chunk.family_name.value, u'')
        self.assertEqual(chunk.qualifier.value, b'')
        self.assertEqual(chunk.timestamp_micros, 0)
        self.assertEqual(chunk.labels, [])

    def test__copy_from_current_blank(self):
        ROW_KEY = b'RK'
        FAMILY_NAME = u'A'
        QUALIFIER = b'C'
        TIMESTAMP_MICROS = 100
        LABELS = ['L1', 'L2']
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        yrd._cell = _PartialCellData()
        chunks = _generate_cell_chunks([''])
        chunk = chunks[0]
        chunk.row_key = ROW_KEY
        chunk.family_name.value = FAMILY_NAME
        chunk.qualifier.value = QUALIFIER
        chunk.timestamp_micros = TIMESTAMP_MICROS
        chunk.labels.extend(LABELS)
        yrd._copy_from_current(chunk)
        self.assertEqual(chunk.row_key, ROW_KEY)
        self.assertEqual(chunk.family_name.value, FAMILY_NAME)
        self.assertEqual(chunk.qualifier.value, QUALIFIER)
        self.assertEqual(chunk.timestamp_micros, TIMESTAMP_MICROS)
        self.assertEqual(chunk.labels, LABELS)

    def test__copy_from_previous_unset(self):
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        cell = _PartialCellData()
        yrd._copy_from_previous(cell)
        self.assertEqual(cell.row_key, '')
        self.assertEqual(cell.family_name, u'')
        self.assertIsNone(cell.qualifier)
        self.assertEqual(cell.timestamp_micros, 0)
        self.assertEqual(cell.labels, [])

    def test__copy_from_previous_blank(self):
        ROW_KEY = 'RK'
        FAMILY_NAME = u'A'
        QUALIFIER = b'C'
        TIMESTAMP_MICROS = 100
        LABELS = ['L1', 'L2']
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        cell = _PartialCellData(
            row_key=ROW_KEY,
            family_name=FAMILY_NAME,
            qualifier=QUALIFIER,
            timestamp_micros=TIMESTAMP_MICROS,
            labels=LABELS,
        )
        yrd._previous_cell = _PartialCellData()
        yrd._copy_from_previous(cell)
        self.assertEqual(cell.row_key, ROW_KEY)
        self.assertEqual(cell.family_name, FAMILY_NAME)
        self.assertEqual(cell.qualifier, QUALIFIER)
        self.assertEqual(cell.timestamp_micros, TIMESTAMP_MICROS)
        self.assertEqual(cell.labels, LABELS)

    def test__copy_from_previous_filled(self):
        ROW_KEY = 'RK'
        FAMILY_NAME = u'A'
        QUALIFIER = b'C'
        TIMESTAMP_MICROS = 100
        LABELS = ['L1', 'L2']
        client = _Client()
        client._data_stub = mock.MagicMock()
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        yrd._previous_cell = _PartialCellData(
            row_key=ROW_KEY,
            family_name=FAMILY_NAME,
            qualifier=QUALIFIER,
            timestamp_micros=TIMESTAMP_MICROS,
            labels=LABELS,
        )
        cell = _PartialCellData()
        yrd._copy_from_previous(cell)
        self.assertEqual(cell.row_key, ROW_KEY)
        self.assertEqual(cell.family_name, FAMILY_NAME)
        self.assertEqual(cell.qualifier, QUALIFIER)
        self.assertEqual(cell.timestamp_micros, 0)
        self.assertEqual(cell.labels, [])

    def test_invalid_last_scanned_row_key_on_start(self):
        from google.cloud.bigtable.row_data import InvalidReadRowsResponse

        client = _Client()
        response = _ReadRowsResponseV2(chunks=(), last_scanned_row_key='ABC')
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        with self.assertRaises(InvalidReadRowsResponse):
            self._consume_all(yrd)

    def test_valid_last_scanned_row_key_on_start(self):
        client = _Client()
        response = _ReadRowsResponseV2(
            chunks=(), last_scanned_row_key='AFTER')
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        yrd.last_scanned_row_key = 'BEFORE'
        self._consume_all(yrd)
        self.assertEqual(yrd.last_scanned_row_key, 'AFTER')

    def test_invalid_empty_chunk(self):
        from google.cloud.bigtable.row_data import InvalidChunk

        client = _Client()
        chunks = _generate_cell_chunks([''])
        response = _ReadRowsResponseV2(chunks)
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        yrd = self._make_one(client._data_stub.ReadRows, request)
        with self.assertRaises(InvalidChunk):
            self._consume_all(yrd)

    def test_yield_rows_data(self):
        client = _Client()

        chunk = _ReadRowsResponseCellChunkPB(
            row_key=self.ROW_KEY,
            family_name=self.FAMILY_NAME,
            qualifier=self.QUALIFIER,
            timestamp_micros=self.TIMESTAMP_MICROS,
            value=self.VALUE,
            commit_row=True,
        )
        chunks = [chunk]

        response = _ReadRowsResponseV2(chunks)
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]

        request = object()

        yrd = self._make_one(client._data_stub.ReadRows, request)

        rows = []
        for row in yrd.read_rows():
            rows.append(row)
        result = rows[0]

        self.assertEqual(result.row_key, self.ROW_KEY)

    def _consume_all(self, yrd):
        return [row.row_key for row in yrd.read_rows()]


class TestPartialRowsData_JSON_acceptance_tests(unittest.TestCase):

    _json_tests = None

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.row_data import PartialRowsData

        return PartialRowsData

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _load_json_test(self, test_name):
        import os

        if self.__class__._json_tests is None:
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, 'read-rows-acceptance-test.json')
            raw = _parse_readrows_acceptance_tests(filename)
            tests = self.__class__._json_tests = {}
            for (name, chunks, results) in raw:
                tests[name] = chunks, results
        return self.__class__._json_tests[test_name]

    # JSON Error cases:  invalid chunks

    def _fail_during_consume(self, testcase_name):
        from google.cloud.bigtable.row_data import InvalidChunk

        client = _Client()
        chunks, results = self._load_json_test(testcase_name)
        response = _ReadRowsResponseV2(chunks)
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        prd = self._make_one(client._data_stub.ReadRows, request)
        with self.assertRaises(InvalidChunk):
            prd.consume_all()
        expected_result = self._sort_flattend_cells(
            [result for result in results if not result['error']])
        flattened = self._sort_flattend_cells(_flatten_cells(prd))
        self.assertEqual(flattened, expected_result)

    def test_invalid_no_cell_key_before_commit(self):
        self._fail_during_consume('invalid - no cell key before commit')

    def test_invalid_no_cell_key_before_value(self):
        self._fail_during_consume('invalid - no cell key before value')

    def test_invalid_new_col_family_wo_qualifier(self):
        self._fail_during_consume(
            'invalid - new col family must specify qualifier')

    def test_invalid_no_commit_between_rows(self):
        self._fail_during_consume('invalid - no commit between rows')

    def test_invalid_no_commit_after_first_row(self):
        self._fail_during_consume('invalid - no commit after first row')

    def test_invalid_duplicate_row_key(self):
        self._fail_during_consume('invalid - duplicate row key')

    def test_invalid_new_row_missing_row_key(self):
        self._fail_during_consume('invalid - new row missing row key')

    def test_invalid_bare_reset(self):
        self._fail_during_consume('invalid - bare reset')

    def test_invalid_bad_reset_no_commit(self):
        self._fail_during_consume('invalid - bad reset, no commit')

    def test_invalid_missing_key_after_reset(self):
        self._fail_during_consume('invalid - missing key after reset')

    def test_invalid_reset_with_chunk(self):
        self._fail_during_consume('invalid - reset with chunk')

    def test_invalid_commit_with_chunk(self):
        self._fail_during_consume('invalid - commit with chunk')

    # JSON Error cases:  incomplete final row

    def _sort_flattend_cells(self, flattened):
        import operator

        key_func = operator.itemgetter('rk', 'fm', 'qual')
        return sorted(flattened, key=key_func)

    def _incomplete_final_row(self, testcase_name):
        client = _Client()
        chunks, results = self._load_json_test(testcase_name)
        response = _ReadRowsResponseV2(chunks)
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        prd = self._make_one(client._data_stub.ReadRows, request)
        prd.consume_all()
        self.assertEqual(prd.state, prd.ROW_IN_PROGRESS)
        expected_result = self._sort_flattend_cells(
            [result for result in results if not result['error']])
        flattened = self._sort_flattend_cells(_flatten_cells(prd))
        self.assertEqual(flattened, expected_result)

    def test_invalid_no_commit(self):
        self._incomplete_final_row('invalid - no commit')

    def test_invalid_last_row_missing_commit(self):
        self._incomplete_final_row('invalid - last row missing commit')

    # Non-error cases

    _marker = object()

    def _match_results(self, testcase_name, expected_result=_marker):
        client = _Client()
        chunks, results = self._load_json_test(testcase_name)
        response = _ReadRowsResponseV2(chunks)
        iterator = _MockCancellableIterator(response)
        client._data_stub = mock.MagicMock()
        client._data_stub.ReadRows.side_effect = [iterator]
        request = object()
        prd = self._make_one(client._data_stub.ReadRows, request)
        prd.consume_all()
        flattened = self._sort_flattend_cells(_flatten_cells(prd))
        if expected_result is self._marker:
            expected_result = self._sort_flattend_cells(results)
        self.assertEqual(flattened, expected_result)

    def test_bare_commit_implies_ts_zero(self):
        self._match_results('bare commit implies ts=0')

    def test_simple_row_with_timestamp(self):
        self._match_results('simple row with timestamp')

    def test_missing_timestamp_implies_ts_zero(self):
        self._match_results('missing timestamp, implied ts=0')

    def test_empty_cell_value(self):
        self._match_results('empty cell value')

    def test_two_unsplit_cells(self):
        self._match_results('two unsplit cells')

    def test_two_qualifiers(self):
        self._match_results('two qualifiers')

    def test_two_families(self):
        self._match_results('two families')

    def test_with_labels(self):
        self._match_results('with labels')

    def test_split_cell_bare_commit(self):
        self._match_results('split cell, bare commit')

    def test_split_cell(self):
        self._match_results('split cell')

    def test_split_four_ways(self):
        self._match_results('split four ways')

    def test_two_split_cells(self):
        self._match_results('two split cells')

    def test_multi_qualifier_splits(self):
        self._match_results('multi-qualifier splits')

    def test_multi_qualifier_multi_split(self):
        self._match_results('multi-qualifier multi-split')

    def test_multi_family_split(self):
        self._match_results('multi-family split')

    def test_two_rows(self):
        self._match_results('two rows')

    def test_two_rows_implicit_timestamp(self):
        self._match_results('two rows implicit timestamp')

    def test_two_rows_empty_value(self):
        self._match_results('two rows empty value')

    def test_two_rows_one_with_multiple_cells(self):
        self._match_results('two rows, one with multiple cells')

    def test_two_rows_multiple_cells_multiple_families(self):
        self._match_results('two rows, multiple cells, multiple families')

    def test_two_rows_multiple_cells(self):
        self._match_results('two rows, multiple cells')

    def test_two_rows_four_cells_two_labels(self):
        self._match_results('two rows, four cells, 2 labels')

    def test_two_rows_with_splits_same_timestamp(self):
        self._match_results('two rows with splits, same timestamp')

    def test_no_data_after_reset(self):
        # JSON testcase has `"results": null`
        self._match_results('no data after reset', expected_result=[])

    def test_simple_reset(self):
        self._match_results('simple reset')

    def test_reset_to_new_val(self):
        self._match_results('reset to new val')

    def test_reset_to_new_qual(self):
        self._match_results('reset to new qual')

    def test_reset_with_splits(self):
        self._match_results('reset with splits')

    def test_two_resets(self):
        self._match_results('two resets')

    def test_reset_to_new_row(self):
        self._match_results('reset to new row')

    def test_reset_in_between_chunks(self):
        self._match_results('reset in between chunks')

    def test_empty_cell_chunk(self):
        self._match_results('empty cell chunk')

    def test_empty_second_qualifier(self):
        self._match_results('empty second qualifier')


def _flatten_cells(prd):
    # Match results format from JSON testcases.
    # Doesn't handle error cases.
    from google.cloud._helpers import _bytes_to_unicode
    from google.cloud._helpers import _microseconds_from_datetime

    for row_key, row in prd.rows.items():
        for family_name, family in row.cells.items():
            for qualifier, column in family.items():
                for cell in column:
                    yield {
                        u'rk': _bytes_to_unicode(row_key),
                        u'fm': family_name,
                        u'qual': _bytes_to_unicode(qualifier),
                        u'ts': _microseconds_from_datetime(cell.timestamp),
                        u'value': _bytes_to_unicode(cell.value),
                        u'label': u' '.join(cell.labels),
                        u'error': False,
                    }


class _MockCancellableIterator(object):

    cancel_calls = 0

    def __init__(self, *values):
        self.iter_values = iter(values)

    def cancel(self):
        self.cancel_calls += 1

    def next(self):
        return next(self.iter_values)

    __next__ = next


class _PartialCellData(object):

    row_key = ''
    family_name = u''
    qualifier = None
    timestamp_micros = 0

    def __init__(self, **kw):
        self.labels = kw.pop('labels', [])
        self.__dict__.update(kw)


class _ReadRowsResponseV2(object):

    def __init__(self, chunks, last_scanned_row_key=''):
        self.chunks = chunks
        self.last_scanned_row_key = last_scanned_row_key


def _generate_cell_chunks(chunk_text_pbs):
    from google.protobuf.text_format import Merge
    from google.cloud.bigtable._generated.bigtable_pb2 import ReadRowsResponse

    chunks = []

    for chunk_text_pb in chunk_text_pbs:
        chunk = ReadRowsResponse.CellChunk()
        chunks.append(Merge(chunk_text_pb, chunk))

    return chunks


def _parse_readrows_acceptance_tests(filename):
    """Parse acceptance tests from JSON

    See
    https://github.com/GoogleCloudPlatform/cloud-bigtable-client/blob/\
    4d3185662ca61bc9fa1bdf1ec0166f6e5ecf86c6/bigtable-client-core/src/\
    test/resources/com/google/cloud/bigtable/grpc/scanner/v2/
    read-rows-acceptance-test.json
    """
    import json

    with open(filename) as json_file:
        test_json = json.load(json_file)

    for test in test_json['tests']:
        name = test['name']
        chunks = _generate_cell_chunks(test['chunks'])
        results = test['results']
        yield name, chunks, results


def _ReadRowsResponseCellChunkPB(*args, **kw):
    from google.cloud.bigtable._generated import (
        bigtable_pb2 as messages_v2_pb2)

    family_name = kw.pop('family_name')
    qualifier = kw.pop('qualifier')
    message = messages_v2_pb2.ReadRowsResponse.CellChunk(*args, **kw)
    message.family_name.value = family_name
    message.qualifier.value = qualifier
    return message
