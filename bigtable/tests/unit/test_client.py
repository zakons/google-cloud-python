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


import unittest

import mock

from ._testing import _make_credentials


class TestClient(unittest.TestCase):

    PROJECT = 'PROJECT'
    INSTANCE_ID = 'instance-id'
    DISPLAY_NAME = 'display-name'
    USER_AGENT = 'you-sir-age-int'

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.client import Client

        return Client

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_constructor_both_admin_and_read_only(self):
        credentials = _make_credentials()
        with self.assertRaises(ValueError):
            self._make_one(
                project=self.PROJECT, credentials=credentials,
                admin=True, read_only=True)

    def test__get_scopes_default(self):
        from google.cloud.bigtable.client import DATA_SCOPE

        client = self._make_one(
            project=self.PROJECT, credentials=_make_credentials())
        self.assertEqual(client._get_scopes(), (DATA_SCOPE,))

    def test__get_scopes_admin(self):
        from google.cloud.bigtable.client import ADMIN_SCOPE
        from google.cloud.bigtable.client import DATA_SCOPE

        client = self._make_one(
            project=self.PROJECT, credentials=_make_credentials(),
            admin=True)
        expected_scopes = (DATA_SCOPE, ADMIN_SCOPE)
        self.assertEqual(client._get_scopes(), expected_scopes)

    def test__get_scopes_read_only(self):
        from google.cloud.bigtable.client import READ_ONLY_SCOPE

        client = self._make_one(
            project=self.PROJECT, credentials=_make_credentials(),
            read_only=True)
        self.assertEqual(client._get_scopes(), (READ_ONLY_SCOPE,))

    def test_credentials_getter(self):
        credentials = _make_credentials()
        project = 'PROJECT'
        client = self._make_one(
            project=project, credentials=credentials)
        self.assertIs(client._credentials,
                      credentials.with_scopes.return_value)

    def test_project_name_property(self):
        credentials = _make_credentials()
        project = 'PROJECT'
        client = self._make_one(project=project, credentials=credentials,
                                admin=True)
        project_name = 'projects/' + project
        self.assertEqual(client.project_path, project_name)

    def test_instance_factory_defaults(self):
        from google.cloud.bigtable.instance import Instance

        PROJECT = 'PROJECT'
        INSTANCE_ID = 'instance-id'
        DISPLAY_NAME = 'display-name'
        credentials = _make_credentials()
        client = self._make_one(
            project=PROJECT, credentials=credentials)

        instance = client.instance(INSTANCE_ID, display_name=DISPLAY_NAME)

        self.assertIsInstance(instance, Instance)
        self.assertEqual(instance.instance_id, INSTANCE_ID)
        self.assertEqual(instance.display_name, DISPLAY_NAME)
        self.assertIs(instance._client, client)

    def test_instance_factory_w_explicit_serve_nodes(self):
        from google.cloud.bigtable.instance import Instance

        PROJECT = 'PROJECT'
        INSTANCE_ID = 'instance-id'
        DISPLAY_NAME = 'display-name'
        credentials = _make_credentials()
        client = self._make_one(
            project=PROJECT, credentials=credentials)

        instance = client.instance(INSTANCE_ID, display_name=DISPLAY_NAME)

        self.assertIsInstance(instance, Instance)
        self.assertEqual(instance.instance_id, INSTANCE_ID)
        self.assertEqual(instance.display_name, DISPLAY_NAME)
        self.assertIs(instance._client, client)

    def test_admin_client_w_value_error(self):
        credentials = _make_credentials()
        client = self._make_one(project=self.PROJECT, credentials=credentials)

        with self.assertRaises(ValueError):
            client.table_admin_client()

        with self.assertRaises(ValueError):
            client.instance_admin_client()

    def test_table_data_client(self):
        credentials = _make_credentials()
        client = self._make_one(project=self.PROJECT, credentials=credentials,
                                admin=True)

        table_data_client = client.table_data_client
        self.assertEqual(client._table_data_client, table_data_client)

        client._table_data_client = object()
        table_data_client = client.table_data_client
        self.assertEqual(client.table_data_client, table_data_client)

    def test_table_admin_client(self):
        credentials = _make_credentials()
        client = self._make_one(project=self.PROJECT, credentials=credentials,
                                admin=True)

        table_admin_client = client.table_admin_client
        self.assertEqual(client._table_admin_client, table_admin_client)

        client._table_admin_client = object()
        table_admin_client = client.table_admin_client
        self.assertEqual(client._table_admin_client, table_admin_client)

    def test_table_data_client_w_value_error(self):
        credentials = _make_credentials()
        client = self._make_one(project=self.PROJECT, credentials=credentials)

        with self.assertRaises(ValueError):
            client.table_data_client()

    def test_list_instances(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_instance_admin_pb2 as messages_v2_pb2)
        from google.cloud.bigtable_admin_v2.gapic import \
            bigtable_instance_admin_client
        from google.cloud.bigtable.instance import Instance

        FAILED_LOCATION = 'FAILED'
        INSTANCE_ID1 = 'instance-id1'
        INSTANCE_ID2 = 'instance-id2'
        INSTANCE_NAME1 = (
                'projects/' + self.PROJECT + '/instances/' + INSTANCE_ID1)
        INSTANCE_NAME2 = (
                'projects/' + self.PROJECT + '/instances/' + INSTANCE_ID2)

        credentials = _make_credentials()
        api = bigtable_instance_admin_client.BigtableInstanceAdminClient(
            mock.Mock())
        client = self._make_one(project=self.PROJECT, credentials=credentials,
                                admin=True)

        # Create response_pb
        response_pb = messages_v2_pb2.ListInstancesResponse(
            failed_locations=[
                FAILED_LOCATION,
            ],
            instances=[
                data_v2_pb2.Instance(
                    name=INSTANCE_NAME1,
                    display_name=INSTANCE_NAME1,
                ),
                data_v2_pb2.Instance(
                    name=INSTANCE_NAME2,
                    display_name=INSTANCE_NAME2,
                ),
            ],
        )

        # Patch the stub used by the API method.
        client._instance_admin_client = api
        bigtable_instance_stub = (
            client.instance_admin_client.bigtable_instance_admin_stub)
        bigtable_instance_stub.ListInstances.side_effect = [response_pb]

        # Perform the method and check the result.
        instances, failed_locations = client.list_instances()

        instance_1, instance_2 = instances

        self.assertIsInstance(instance_1, Instance)
        self.assertEqual(instance_1.name, INSTANCE_NAME1)
        self.assertTrue(instance_1._client is client)

        self.assertIsInstance(instance_2, Instance)
        self.assertEqual(instance_2.name, INSTANCE_NAME2)
        self.assertTrue(instance_2._client is client)

        self.assertEqual(failed_locations, [FAILED_LOCATION])
