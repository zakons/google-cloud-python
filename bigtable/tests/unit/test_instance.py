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


class MultiCallableStub(object):
    """Stub for the grpc.UnaryUnaryMultiCallable interface."""

    def __init__(self, method, channel_stub):
        self.method = method
        self.channel_stub = channel_stub

    def __call__(self, request, timeout=None, metadata=None, credentials=None):
        self.channel_stub.requests.append((self.method, request))

        return self.channel_stub.responses.pop()


class ChannelStub(object):
    """Stub for the grpc.Channel interface."""

    def __init__(self, responses=[]):
        self.responses = responses
        self.requests = []

    def unary_unary(self,
                    method,
                    request_serializer=None,
                    response_deserializer=None):
        return MultiCallableStub(method, self)


class TestInstance(unittest.TestCase):

    PROJECT = 'project'
    INSTANCE_ID = 'instance-id'
    INSTANCE_NAME = 'projects/' + PROJECT + '/instances/' + INSTANCE_ID
    LOCATION_ID = 'locname'
    LOCATION = 'projects/' + PROJECT + '/locations/' + LOCATION_ID
    APP_PROFILE_PATH = (
            'projects/' + PROJECT + '/instances/' + INSTANCE_ID
            + '/appProfiles/')
    DISPLAY_NAME = 'display_name'
    OP_ID = 8915
    OP_NAME = ('operations/projects/%s/instances/%soperations/%d' %
               (PROJECT, INSTANCE_ID, OP_ID))
    TABLE_ID = 'table_id'
    TABLE_NAME = INSTANCE_NAME + '/tables/' + TABLE_ID

    @staticmethod
    def _get_target_class():
        from google.cloud.bigtable.instance import Instance

        return Instance

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    @staticmethod
    def _get_target_client_class():
        from google.cloud.bigtable.client import Client

        return Client

    def _make_client(self, *args, **kwargs):
        return self._get_target_client_class()(*args, **kwargs)

    def test_constructor_defaults(self):

        client = object()
        instance = self._make_one(self.INSTANCE_ID, client)
        self.assertEqual(instance.instance_id, self.INSTANCE_ID)
        self.assertEqual(instance.display_name, self.INSTANCE_ID)
        self.assertIs(instance._client, client)

    def test_constructor_non_default(self):
        display_name = 'display_name'
        client = object()

        instance = self._make_one(self.INSTANCE_ID, client,
                                  display_name=display_name)
        self.assertEqual(instance.instance_id, self.INSTANCE_ID)
        self.assertEqual(instance.display_name, display_name)
        self.assertIs(instance._client, client)

    def test_table_factory(self):
        from google.cloud.bigtable.table import Table

        instance = self._make_one(self.INSTANCE_ID, None)

        table = instance.table(self.TABLE_ID)
        self.assertIsInstance(table, Table)
        self.assertEqual(table.table_id, self.TABLE_ID)
        self.assertEqual(table._instance, instance)

    def test__update_from_pb_success(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)

        display_name = 'display_name'
        instance_pb = data_v2_pb2.Instance(
            display_name=display_name,
        )

        instance = self._make_one(None, None)
        self.assertIsNone(instance.display_name)
        instance._update_from_pb(instance_pb)
        self.assertEqual(instance.display_name, display_name)

    def test__update_from_pb_no_display_name(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)

        instance_pb = data_v2_pb2.Instance()
        instance = self._make_one(None, None)
        self.assertIsNone(instance.display_name)
        with self.assertRaises(ValueError):
            instance._update_from_pb(instance_pb)

    def test_from_pb_success(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)

        client = _Client(project=self.PROJECT)

        instance_pb = data_v2_pb2.Instance(
            name=self.INSTANCE_NAME,
            display_name=self.INSTANCE_ID,
        )

        klass = self._get_target_class()
        instance = klass.from_pb(instance_pb, client)
        self.assertIsInstance(instance, klass)
        self.assertEqual(instance._client, client)
        self.assertEqual(instance.instance_id, self.INSTANCE_ID)

    def test_from_pb_bad_instance_name(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)

        instance_name = 'INCORRECT_FORMAT'
        instance_pb = data_v2_pb2.Instance(name=instance_name)

        klass = self._get_target_class()
        with self.assertRaises(ValueError):
            klass.from_pb(instance_pb, None)

    def test_from_pb_project_mistmatch(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)

        ALT_PROJECT = 'ALT_PROJECT'
        client = _Client(project=ALT_PROJECT)

        self.assertNotEqual(self.PROJECT, ALT_PROJECT)

        instance_pb = data_v2_pb2.Instance(name=self.INSTANCE_NAME)

        klass = self._get_target_class()
        with self.assertRaises(ValueError):
            klass.from_pb(instance_pb, client)

    def test_name_property(self):
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        api = bigtable_instance_admin_client.BigtableInstanceAdminClient(
            mock.Mock())
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)

        # Patch the the API method.
        client._instance_admin_client = api

        instance = self._make_one(self.INSTANCE_ID, client)
        self.assertEqual(instance.name, self.INSTANCE_NAME)

    def test___eq__(self):
        client = object()
        instance1 = self._make_one(self.INSTANCE_ID, client)
        instance2 = self._make_one(self.INSTANCE_ID, client)
        self.assertEqual(instance1, instance2)

    def test___eq__type_differ(self):
        client = object()
        instance1 = self._make_one(self.INSTANCE_ID, client)
        instance2 = object()
        self.assertNotEqual(instance1, instance2)

    def test___ne__same_value(self):
        client = object()
        instance1 = self._make_one(self.INSTANCE_ID, client)
        instance2 = self._make_one(self.INSTANCE_ID, client)
        comparison_val = (instance1 != instance2)
        self.assertFalse(comparison_val)

    def test___ne__(self):
        instance1 = self._make_one('instance_id1', 'client1')
        instance2 = self._make_one('instance_id2', 'client2')
        self.assertNotEqual(instance1, instance2)

    def test_reload(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as data_v2_pb2)
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        api = bigtable_instance_admin_client.BigtableInstanceAdminClient(
            mock.Mock())
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Create response_pb
        DISPLAY_NAME = u'hey-hi-hello'
        response_pb = data_v2_pb2.Instance(
            display_name=DISPLAY_NAME,
        )

        # Patch the stub used by the API method.
        client._instance_admin_client = api
        bigtable_instance_stub = (
            client._instance_admin_client.bigtable_instance_admin_stub)
        bigtable_instance_stub.GetInstance.side_effect = [response_pb]

        # Create expected_result.
        expected_result = None  # reload() has no return value.

        # Check Instance optional config values before.
        self.assertEqual(instance.display_name, self.INSTANCE_ID)

        # Perform the method and check the result.
        result = instance.reload()
        self.assertEqual(result, expected_result)

        # Check Instance optional config values before.
        self.assertEqual(instance.display_name, DISPLAY_NAME)

    def test_create(self):
        import datetime
        from google.api_core import operation
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_instance_admin_pb2 as messages_v2_pb2)
        from google.cloud._helpers import _datetime_to_pb_timestamp
        from google.cloud.bigtable_admin_v2 import enums
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)
        from google.cloud.bigtable.cluster import DEFAULT_SERVE_NODES

        NOW = datetime.datetime.utcnow()
        NOW_PB = _datetime_to_pb_timestamp(NOW)
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client,
                                  display_name=self.DISPLAY_NAME)

        # Create response_pb
        metadata = messages_v2_pb2.CreateInstanceMetadata(request_time=NOW_PB)
        type_url = 'type.googleapis.com/%s' % (
            messages_v2_pb2.CreateInstanceMetadata.DESCRIPTOR.full_name,)
        response_pb = operations_pb2.Operation(
            name=self.OP_NAME,
            metadata=Any(
                type_url=type_url,
                value=metadata.SerializeToString(),
            )
        )

        # Patch the stub used by the API method.
        channel = ChannelStub(responses=[response_pb])
        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                channel=channel))
        client._instance_admin_client = instance_api

        # Perform the method and check the result.
        result = instance.create(location_id=self.LOCATION_ID)
        actual_request = channel.requests[0][1]

        cluster_id = '{}-cluster'.format(self.INSTANCE_ID)
        cluster = self._create_cluster(
            instance_api, cluster_id, self.LOCATION_ID, DEFAULT_SERVE_NODES,
            enums.StorageType.STORAGE_TYPE_UNSPECIFIED)

        expected_request = self._create_instance_request(
            self.DISPLAY_NAME,
            {cluster_id: cluster}
        )
        self.assertEqual(expected_request, actual_request)
        self.assertIsInstance(result, operation.Operation)
        # self.assertEqual(result.operation.name, self.OP_NAME)
        self.assertIsInstance(result.metadata,
                              messages_v2_pb2.CreateInstanceMetadata)

    def test_create_w_explicit_serve_nodes(self):
        from google.api_core import operation
        from google.longrunning import operations_pb2
        from google.cloud.bigtable_admin_v2 import enums
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        serve_nodes = 10
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client,
                                  display_name=self.DISPLAY_NAME)

        # Create response_pb
        response_pb = operations_pb2.Operation(name=self.OP_NAME)

        # Patch the stub used by the API method.
        channel = ChannelStub(responses=[response_pb])
        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                channel=channel))
        client._instance_admin_client = instance_api

        # Perform the method and check the result.
        result = instance.create(
            location_id=self.LOCATION_ID, serve_nodes=serve_nodes,
            default_storage_type=enums.StorageType.SSD)
        actual_request = channel.requests[0][1]

        cluster_id = '{}-cluster'.format(self.INSTANCE_ID)
        cluster = self._create_cluster(
            instance_api, cluster_id, self.LOCATION_ID, serve_nodes,
            enums.StorageType.SSD)

        expected_request = self._create_instance_request(
            self.DISPLAY_NAME,
            {cluster_id: cluster}
        )
        self.assertEqual(expected_request, actual_request)
        self.assertIsInstance(result, operation.Operation)

    def _create_cluster(self, instance_api, cluster_id, location_id,
                        server_nodes, storage_type):
        from google.cloud.bigtable_admin_v2.types import instance_pb2

        cluster_name = instance_api.cluster_path(
            self.PROJECT, self.INSTANCE_ID, cluster_id)
        location = instance_api.location_path(
            self.PROJECT, location_id)
        return instance_pb2.Cluster(
            name=cluster_name, location=location,
            serve_nodes=server_nodes,
            default_storage_type=storage_type)

    def _create_instance_request(self, display_name, clusters):
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_instance_admin_pb2 as messages_v2_pb2)
        from google.cloud.bigtable_admin_v2.types import instance_pb2

        instance = instance_pb2.Instance(display_name=display_name)

        return messages_v2_pb2.CreateInstanceRequest(
            parent='projects/%s' % (self.PROJECT),
            instance_id=self.INSTANCE_ID,
            instance=instance,
            clusters=clusters
        )

    def test_update(self):
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        api = bigtable_instance_admin_client.BigtableInstanceAdminClient(
            mock.Mock())
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client,
                                  display_name=self.DISPLAY_NAME)

        # Mock api calls
        client._instance_admin_client = api

        # Create expected_result.
        expected_result = None

        # Perform the method and check the result.
        result = instance.update()

        self.assertEqual(result, expected_result)

    def test_delete(self):
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        api = bigtable_instance_admin_client.BigtableInstanceAdminClient(
            mock.Mock())
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Mock api calls
        client._instance_admin_client = api

        # Create expected_result.
        expected_result = None  # delete() has no return value.

        # Perform the method and check the result.
        result = instance.delete()

        self.assertEqual(result, expected_result)

    def _list_tables_helper(self, table_name=None):
        from google.cloud.bigtable_admin_v2.proto import (
            table_pb2 as table_data_v2_pb2)
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_table_admin_pb2 as table_messages_v1_pb2)
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_table_admin_client, bigtable_instance_admin_client)

        table_api = bigtable_table_admin_client.BigtableTableAdminClient(
            mock.Mock())
        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                mock.Mock()))
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Create response_pb
        if table_name is None:
            table_name = self.TABLE_NAME

        response_pb = table_messages_v1_pb2.ListTablesResponse(
            tables=[
                table_data_v2_pb2.Table(name=table_name),
            ],
        )

        # Patch the stub used by the API method.
        client._table_admin_client = table_api
        client._instance_admin_client = instance_api
        bigtable_table_stub = (
            client._table_admin_client.bigtable_table_admin_stub)
        bigtable_table_stub.ListTables.side_effect = [response_pb]

        # Create expected_result.
        expected_table = instance.table(self.TABLE_ID)
        expected_result = [expected_table]

        # Perform the method and check the result.
        result = instance.list_tables()

        self.assertEqual(result, expected_result)

    def test_list_tables(self):
        self._list_tables_helper()

    def test_list_tables_failure_bad_split(self):
        with self.assertRaises(ValueError):
            self._list_tables_helper(table_name='wrong-format')

    def test_list_tables_failure_name_bad_before(self):
        BAD_TABLE_NAME = ('nonempty-section-before' +
                          'projects/' + self.PROJECT +
                          '/instances/' + self.INSTANCE_ID +
                          '/tables/' + self.TABLE_ID)
        with self.assertRaises(ValueError):
            self._list_tables_helper(table_name=BAD_TABLE_NAME)

    def test_create_app_profile_with_wrong_routing_policy(self):
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        app_profile_id = 'appProfileId1262094415'
        update_mask = []

        # Create AppProfile with exception
        with self.assertRaises(ValueError):
            instance.create_app_profile(app_profile_id=app_profile_id,
                                        routing_policy_type=None)

        with self.assertRaises(ValueError):
            instance.update_app_profile(app_profile_id,
                                        update_mask=update_mask,
                                        routing_policy_type=None)

    def test_create_app_profile_with_multi_routing_policy(self):
        from google.cloud.bigtable_admin_v2.proto import instance_pb2
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        description = 'description-1724546052'
        app_profile_id = 'appProfileId1262094415'
        expected_response = {
            'name': self.APP_PROFILE_PATH + app_profile_id,
            'description': description,
            'multi_cluster_routing_use_any':
                instance_pb2.AppProfile.MultiClusterRoutingUseAny()
        }
        expected_request = {
            'app_profile_id': app_profile_id,
            'routing_policy_type': 1,
            'description': description
        }
        expected_response = instance_pb2.AppProfile(**expected_response)

        channel = ChannelStub(responses=[expected_response])
        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                channel=channel))

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api

        # Perform the method and check the result.
        result = instance.create_app_profile(**expected_request)

        parent = client._instance_admin_client.instance_path(
            self.PROJECT, self.INSTANCE_ID)
        expected_request = _CreateAppProfileRequestPB(
            parent=parent, app_profile_id=app_profile_id,
            app_profile=expected_response,
        )

        actual_request = channel.requests[0][1]
        assert expected_request == actual_request
        self.assertEqual(result, expected_response)

    def test_create_app_profile_with_single_routing_policy(self):
        from google.cloud.bigtable_admin_v2.proto import instance_pb2
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        description = 'description-1724546052'
        app_profile_id = 'appProfileId1262094415'
        cluster_id = 'cluster-id'
        expected_response = {
            'name': self.APP_PROFILE_PATH + app_profile_id,
            'description': description,
            'single_cluster_routing':
                instance_pb2.AppProfile.SingleClusterRouting(
                    cluster_id=cluster_id,
                    allow_transactional_writes=False
                )
        }
        expected_request = {
            'app_profile_id': app_profile_id,
            'routing_policy_type': 2,
            'description': description,
            'cluster_id': cluster_id
        }
        expected_response = instance_pb2.AppProfile(**expected_response)

        channel = ChannelStub(responses=[expected_response])
        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                channel=channel))

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api

        # Perform the method and check the result.
        result = instance.create_app_profile(**expected_request)

        parent = client._instance_admin_client.instance_path(
            self.PROJECT, self.INSTANCE_ID)
        expected_request = _CreateAppProfileRequestPB(
            parent=parent, app_profile_id=app_profile_id,
            app_profile=expected_response,
        )

        actual_request = channel.requests[0][1]
        assert expected_request == actual_request
        self.assertEqual(result, expected_response)

    def test_get_app_profile(self):
        from google.cloud.bigtable_admin_v2.proto import (
            instance_pb2 as instance_data_v2_pb2)
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                mock.Mock()))

        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        name = 'name3373707'
        etag = 'etag3123477'
        description = 'description-1724546052'
        expected_response = {
            'name': name,
            'etag': etag,
            'description': description
        }
        expected_response = instance_data_v2_pb2.AppProfile(
            **expected_response)

        response_pb = instance_data_v2_pb2.AppProfile(
            name=name,
            etag=etag,
            description=description
        )

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api
        bigtable_instance_stub = (
            client._instance_admin_client.bigtable_instance_admin_stub)
        bigtable_instance_stub.GetAppProfile.side_effect = [response_pb]

        # Perform the method and check the result.
        app_profile_id = 'appProfileId1262094415'
        result = instance.get_app_profile(app_profile_id=app_profile_id)

        self.assertEqual(result, expected_response)

    def test_list_app_profiles(self):
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_instance_admin_pb2 as instance_messages_v1_pb2)
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                mock.Mock()))

        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Setup Expected Response
        next_page_token = ''
        app_profiles_element = {}
        app_profiles = [app_profiles_element]
        expected_response = {
            'next_page_token': next_page_token,
            'app_profiles': app_profiles
        }
        expected_response = instance_messages_v1_pb2.ListAppProfilesResponse(
            **expected_response)

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api
        bigtable_instance_stub = (
            client._instance_admin_client.bigtable_instance_admin_stub)
        bigtable_instance_stub.ListAppProfiles.side_effect = [
            expected_response]

        # Perform the method and check the result.
        response = instance.list_app_profiles()

        self.assertEqual(response[0], expected_response.app_profiles[0])

    def test_update_app_profile(self):
        import datetime
        from google.api_core import operation
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_instance_admin_pb2 as messages_v2_pb2)
        from google.cloud._helpers import _datetime_to_pb_timestamp
        from tests.unit._testing import _FakeStub
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                mock.Mock()))

        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Create response_pb
        NOW = datetime.datetime.utcnow()
        NOW_PB = _datetime_to_pb_timestamp(NOW)
        metadata = messages_v2_pb2.CreateInstanceMetadata(request_time=NOW_PB)
        type_url = 'type.googleapis.com/%s' % (
            messages_v2_pb2.CreateInstanceMetadata.DESCRIPTOR.full_name,)
        response_pb = operations_pb2.Operation(
            name=self.OP_NAME,
            metadata=Any(
                type_url=type_url,
                value=metadata.SerializeToString(),
            )
        )

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api
        stub = _FakeStub(response_pb)
        client._instance_admin_client.bigtable_instance_admin_stub = stub
        update_mask = []

        # Perform the method and check the result.
        app_profile_id = 'appProfileId1262094415'
        result = instance.update_app_profile(app_profile_id,
                                             update_mask=update_mask,
                                             routing_policy_type=1)

        self.assertIsInstance(result, operation.Operation)

    def test_update_app_profile_with_single_routing_policy(self):
        import datetime
        from google.api_core import operation
        from google.longrunning import operations_pb2
        from google.protobuf.any_pb2 import Any
        from google.cloud.bigtable_admin_v2.proto import (
            bigtable_instance_admin_pb2 as messages_v2_pb2)
        from google.cloud._helpers import _datetime_to_pb_timestamp
        from tests.unit._testing import _FakeStub
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                mock.Mock()))

        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Create response_pb
        NOW = datetime.datetime.utcnow()
        NOW_PB = _datetime_to_pb_timestamp(NOW)
        metadata = messages_v2_pb2.CreateInstanceMetadata(request_time=NOW_PB)
        type_url = 'type.googleapis.com/%s' % (
            messages_v2_pb2.CreateInstanceMetadata.DESCRIPTOR.full_name,)
        response_pb = operations_pb2.Operation(
            name=self.OP_NAME,
            metadata=Any(
                type_url=type_url,
                value=metadata.SerializeToString(),
            )
        )

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api
        stub = _FakeStub(response_pb)
        client._instance_admin_client.bigtable_instance_admin_stub = stub
        update_mask = []

        # Perform the method and check the result.
        app_profile_id = 'appProfileId1262094415'
        cluster_id = 'cluster-id'
        result = instance.update_app_profile(app_profile_id,
                                             update_mask=update_mask,
                                             routing_policy_type=2,
                                             cluster_id=cluster_id)

        self.assertIsInstance(result, operation.Operation)

    def test_delete_app_profile(self):
        from google.cloud.bigtable_admin_v2.gapic import (
            bigtable_instance_admin_client)

        instance_api = (
            bigtable_instance_admin_client.BigtableInstanceAdminClient(
                mock.Mock()))
        credentials = _make_credentials()
        client = self._make_client(project=self.PROJECT,
                                   credentials=credentials, admin=True)
        instance = self._make_one(self.INSTANCE_ID, client)

        # Patch the stub used by the API method.
        client._instance_admin_client = instance_api

        ignore_warnings = True

        expected_result = None  # delete() has no return value.

        app_profile_id = 'appProfileId1262094415'
        result = instance.delete_app_profile(app_profile_id, ignore_warnings)

        self.assertEqual(expected_result, result)


class _Client(object):

    def __init__(self, project):
        self.project = project
        self.project_name = 'projects/' + self.project
        self._operations_stub = mock.sentinel.operations_stub

    def __eq__(self, other):
        return (other.project == self.project and
                other.project_name == self.project_name)


def _CreateAppProfileRequestPB(*args, **kw):
    from google.cloud.bigtable_admin_v2.proto import (
        bigtable_instance_admin_pb2 as instance_v2_pb2)

    return instance_v2_pb2.CreateAppProfileRequest(*args, **kw)
