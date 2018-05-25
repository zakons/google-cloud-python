# Copyright 2014 Google LLC
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

import datetime
import unittest

import mock


def _create_signing_credentials():
    import google.auth.credentials

    class _SigningCredentials(
            google.auth.credentials.Credentials,
            google.auth.credentials.Signing):
        pass

    credentials = mock.Mock(spec=_SigningCredentials)

    return credentials


class Test_Bucket(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from google.cloud.storage.bucket import Bucket
        return Bucket

    def _make_one(
            self, client=None, name=None, properties=None, user_project=None):
        if client is None:
            connection = _Connection()
            client = _Client(connection)
        if user_project is None:
            bucket = self._get_target_class()(client, name=name)
        else:
            bucket = self._get_target_class()(
                client, name=name, user_project=user_project)
        bucket._properties = properties or {}
        return bucket

    def test_ctor(self):
        NAME = 'name'
        properties = {'key': 'value'}
        bucket = self._make_one(name=NAME, properties=properties)
        self.assertEqual(bucket.name, NAME)
        self.assertEqual(bucket._properties, properties)
        self.assertFalse(bucket._acl.loaded)
        self.assertIs(bucket._acl.bucket, bucket)
        self.assertFalse(bucket._default_object_acl.loaded)
        self.assertIs(bucket._default_object_acl.bucket, bucket)
        self.assertIsNone(bucket.user_project)

    def test_ctor_w_user_project(self):
        NAME = 'name'
        USER_PROJECT = 'user-project-123'
        connection = _Connection()
        client = _Client(connection)
        bucket = self._make_one(client, name=NAME, user_project=USER_PROJECT)
        self.assertEqual(bucket.name, NAME)
        self.assertEqual(bucket._properties, {})
        self.assertEqual(bucket.user_project, USER_PROJECT)
        self.assertFalse(bucket._acl.loaded)
        self.assertIs(bucket._acl.bucket, bucket)
        self.assertFalse(bucket._default_object_acl.loaded)
        self.assertIs(bucket._default_object_acl.bucket, bucket)

    def test_blob_wo_keys(self):
        from google.cloud.storage.blob import Blob

        BUCKET_NAME = 'BUCKET_NAME'
        BLOB_NAME = 'BLOB_NAME'
        CHUNK_SIZE = 1024 * 1024

        bucket = self._make_one(name=BUCKET_NAME)
        blob = bucket.blob(
            BLOB_NAME, chunk_size=CHUNK_SIZE)
        self.assertIsInstance(blob, Blob)
        self.assertIs(blob.bucket, bucket)
        self.assertIs(blob.client, bucket.client)
        self.assertEqual(blob.name, BLOB_NAME)
        self.assertEqual(blob.chunk_size, CHUNK_SIZE)
        self.assertIsNone(blob._encryption_key)
        self.assertIsNone(blob.kms_key_name)

    def test_blob_w_encryption_key(self):
        from google.cloud.storage.blob import Blob

        BUCKET_NAME = 'BUCKET_NAME'
        BLOB_NAME = 'BLOB_NAME'
        CHUNK_SIZE = 1024 * 1024
        KEY = b'01234567890123456789012345678901'  # 32 bytes

        bucket = self._make_one(name=BUCKET_NAME)
        blob = bucket.blob(
            BLOB_NAME, chunk_size=CHUNK_SIZE, encryption_key=KEY)
        self.assertIsInstance(blob, Blob)
        self.assertIs(blob.bucket, bucket)
        self.assertIs(blob.client, bucket.client)
        self.assertEqual(blob.name, BLOB_NAME)
        self.assertEqual(blob.chunk_size, CHUNK_SIZE)
        self.assertEqual(blob._encryption_key, KEY)
        self.assertIsNone(blob.kms_key_name)

    def test_blob_w_kms_key_name(self):
        from google.cloud.storage.blob import Blob

        BUCKET_NAME = 'BUCKET_NAME'
        BLOB_NAME = 'BLOB_NAME'
        CHUNK_SIZE = 1024 * 1024
        KMS_RESOURCE = (
            "projects/test-project-123/"
            "locations/us/"
            "keyRings/test-ring/"
            "cryptoKeys/test-key"
        )

        bucket = self._make_one(name=BUCKET_NAME)
        blob = bucket.blob(
            BLOB_NAME, chunk_size=CHUNK_SIZE, kms_key_name=KMS_RESOURCE)
        self.assertIsInstance(blob, Blob)
        self.assertIs(blob.bucket, bucket)
        self.assertIs(blob.client, bucket.client)
        self.assertEqual(blob.name, BLOB_NAME)
        self.assertEqual(blob.chunk_size, CHUNK_SIZE)
        self.assertIsNone(blob._encryption_key)
        self.assertEqual(blob.kms_key_name, KMS_RESOURCE)

    def test_notification_defaults(self):
        from google.cloud.storage.notification import BucketNotification
        from google.cloud.storage.notification import NONE_PAYLOAD_FORMAT

        PROJECT = 'PROJECT'
        BUCKET_NAME = 'BUCKET_NAME'
        TOPIC_NAME = 'TOPIC_NAME'
        client = _Client(_Connection(), project=PROJECT)
        bucket = self._make_one(client, name=BUCKET_NAME)

        notification = bucket.notification(TOPIC_NAME)

        self.assertIsInstance(notification, BucketNotification)
        self.assertIs(notification.bucket, bucket)
        self.assertEqual(notification.topic_project, PROJECT)
        self.assertIsNone(notification.custom_attributes)
        self.assertIsNone(notification.event_types)
        self.assertIsNone(notification.blob_name_prefix)
        self.assertEqual(notification.payload_format, NONE_PAYLOAD_FORMAT)

    def test_notification_explicit(self):
        from google.cloud.storage.notification import (
            BucketNotification,
            OBJECT_FINALIZE_EVENT_TYPE,
            OBJECT_DELETE_EVENT_TYPE,
            JSON_API_V1_PAYLOAD_FORMAT)

        PROJECT = 'PROJECT'
        BUCKET_NAME = 'BUCKET_NAME'
        TOPIC_NAME = 'TOPIC_NAME'
        TOPIC_ALT_PROJECT = 'topic-project-456'
        CUSTOM_ATTRIBUTES = {
            'attr1': 'value1',
            'attr2': 'value2',
        }
        EVENT_TYPES = [OBJECT_FINALIZE_EVENT_TYPE, OBJECT_DELETE_EVENT_TYPE]
        BLOB_NAME_PREFIX = 'blob-name-prefix/'
        client = _Client(_Connection(), project=PROJECT)
        bucket = self._make_one(client, name=BUCKET_NAME)

        notification = bucket.notification(
            TOPIC_NAME,
            topic_project=TOPIC_ALT_PROJECT,
            custom_attributes=CUSTOM_ATTRIBUTES,
            event_types=EVENT_TYPES,
            blob_name_prefix=BLOB_NAME_PREFIX,
            payload_format=JSON_API_V1_PAYLOAD_FORMAT,
        )

        self.assertIsInstance(notification, BucketNotification)
        self.assertIs(notification.bucket, bucket)
        self.assertEqual(notification.topic_project, TOPIC_ALT_PROJECT)
        self.assertEqual(notification.custom_attributes, CUSTOM_ATTRIBUTES)
        self.assertEqual(notification.event_types, EVENT_TYPES)
        self.assertEqual(notification.blob_name_prefix, BLOB_NAME_PREFIX)
        self.assertEqual(
            notification.payload_format, JSON_API_V1_PAYLOAD_FORMAT)

    def test_bucket_name_value(self):
        BUCKET_NAME = 'bucket-name'
        self._make_one(name=BUCKET_NAME)

        bad_start_bucket_name = '/testing123'
        with self.assertRaises(ValueError):
            self._make_one(name=bad_start_bucket_name)

        bad_end_bucket_name = 'testing123/'
        with self.assertRaises(ValueError):
            self._make_one(name=bad_end_bucket_name)

    def test_user_project(self):
        BUCKET_NAME = 'name'
        USER_PROJECT = 'user-project-123'
        bucket = self._make_one(name=BUCKET_NAME)
        bucket._user_project = USER_PROJECT
        self.assertEqual(bucket.user_project, USER_PROJECT)

    def test_exists_miss(self):
        from google.cloud.exceptions import NotFound

        class _FakeConnection(object):

            _called_with = []

            @classmethod
            def api_request(cls, *args, **kwargs):
                cls._called_with.append((args, kwargs))
                raise NotFound(args)

        BUCKET_NAME = 'bucket-name'
        bucket = self._make_one(name=BUCKET_NAME)
        client = _Client(_FakeConnection)
        self.assertFalse(bucket.exists(client=client))
        expected_called_kwargs = {
            'method': 'GET',
            'path': bucket.path,
            'query_params': {
                'fields': 'name',
            },
            '_target_object': None,
        }
        expected_cw = [((), expected_called_kwargs)]
        self.assertEqual(_FakeConnection._called_with, expected_cw)

    def test_exists_hit_w_user_project(self):
        USER_PROJECT = 'user-project-123'

        class _FakeConnection(object):

            _called_with = []

            @classmethod
            def api_request(cls, *args, **kwargs):
                cls._called_with.append((args, kwargs))
                # exists() does not use the return value
                return object()

        BUCKET_NAME = 'bucket-name'
        bucket = self._make_one(name=BUCKET_NAME, user_project=USER_PROJECT)
        client = _Client(_FakeConnection)
        self.assertTrue(bucket.exists(client=client))
        expected_called_kwargs = {
            'method': 'GET',
            'path': bucket.path,
            'query_params': {
                'fields': 'name',
                'userProject': USER_PROJECT,
            },
            '_target_object': None,
        }
        expected_cw = [((), expected_called_kwargs)]
        self.assertEqual(_FakeConnection._called_with, expected_cw)

    def test_create_w_user_project(self):
        PROJECT = 'PROJECT'
        BUCKET_NAME = 'bucket-name'
        USER_PROJECT = 'user-project-123'
        connection = _Connection()
        client = _Client(connection, project=PROJECT)
        bucket = self._make_one(client, BUCKET_NAME, user_project=USER_PROJECT)

        with self.assertRaises(ValueError):
            bucket.create()

    def test_create_w_missing_client_project(self):
        BUCKET_NAME = 'bucket-name'
        connection = _Connection()
        client = _Client(connection, project=None)
        bucket = self._make_one(client, BUCKET_NAME)

        with self.assertRaises(ValueError):
            bucket.create()

    def test_create_w_explicit_project(self):
        PROJECT = 'PROJECT'
        BUCKET_NAME = 'bucket-name'
        OTHER_PROJECT = 'other-project-123'
        DATA = {'name': BUCKET_NAME}
        connection = _Connection(DATA)
        client = _Client(connection, project=PROJECT)
        bucket = self._make_one(client, BUCKET_NAME)

        bucket.create(project=OTHER_PROJECT)

        kw, = connection._requested
        self.assertEqual(kw['method'], 'POST')
        self.assertEqual(kw['path'], '/b')
        self.assertEqual(kw['query_params'], {'project': OTHER_PROJECT})
        self.assertEqual(kw['data'], DATA)

    def test_create_hit(self):
        PROJECT = 'PROJECT'
        BUCKET_NAME = 'bucket-name'
        DATA = {'name': BUCKET_NAME}
        connection = _Connection(DATA)
        client = _Client(connection, project=PROJECT)
        bucket = self._make_one(client=client, name=BUCKET_NAME)
        bucket.create()

        kw, = connection._requested
        self.assertEqual(kw['method'], 'POST')
        self.assertEqual(kw['path'], '/b')
        self.assertEqual(kw['query_params'], {'project': PROJECT})
        self.assertEqual(kw['data'], DATA)

    def test_create_w_extra_properties(self):
        BUCKET_NAME = 'bucket-name'
        PROJECT = 'PROJECT'
        CORS = [{
            'maxAgeSeconds': 60,
            'methods': ['*'],
            'origin': ['https://example.com/frontend'],
            'responseHeader': ['X-Custom-Header'],
        }]
        LIFECYCLE_RULES = [{
            "action": {"type": "Delete"},
            "condition": {"age": 365}
        }]
        LOCATION = 'eu'
        LABELS = {'color': 'red', 'flavor': 'cherry'}
        STORAGE_CLASS = 'NEARLINE'
        DATA = {
            'name': BUCKET_NAME,
            'cors': CORS,
            'lifecycle': {'rule': LIFECYCLE_RULES},
            'location': LOCATION,
            'storageClass': STORAGE_CLASS,
            'versioning': {'enabled': True},
            'billing': {'requesterPays': True},
            'labels': LABELS,
        }
        connection = _Connection(DATA)
        client = _Client(connection, project=PROJECT)
        bucket = self._make_one(client=client, name=BUCKET_NAME)
        bucket.cors = CORS
        bucket.lifecycle_rules = LIFECYCLE_RULES
        bucket.location = LOCATION
        bucket.storage_class = STORAGE_CLASS
        bucket.versioning_enabled = True
        bucket.requester_pays = True
        bucket.labels = LABELS
        bucket.create()

        kw, = connection._requested
        self.assertEqual(kw['method'], 'POST')
        self.assertEqual(kw['path'], '/b')
        self.assertEqual(kw['query_params'], {'project': PROJECT})
        self.assertEqual(kw['data'], DATA)

    def test_acl_property(self):
        from google.cloud.storage.acl import BucketACL

        bucket = self._make_one()
        acl = bucket.acl
        self.assertIsInstance(acl, BucketACL)
        self.assertIs(acl, bucket._acl)

    def test_default_object_acl_property(self):
        from google.cloud.storage.acl import DefaultObjectACL

        bucket = self._make_one()
        acl = bucket.default_object_acl
        self.assertIsInstance(acl, DefaultObjectACL)
        self.assertIs(acl, bucket._default_object_acl)

    def test_path_no_name(self):
        bucket = self._make_one()
        self.assertRaises(ValueError, getattr, bucket, 'path')

    def test_path_w_name(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        self.assertEqual(bucket.path, '/b/%s' % NAME)

    def test_get_blob_miss(self):
        NAME = 'name'
        NONESUCH = 'nonesuch'
        connection = _Connection()
        client = _Client(connection)
        bucket = self._make_one(name=NAME)
        result = bucket.get_blob(NONESUCH, client=client)
        self.assertIsNone(result)
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], '/b/%s/o/%s' % (NAME, NONESUCH))

    def test_get_blob_hit_w_user_project(self):
        NAME = 'name'
        BLOB_NAME = 'blob-name'
        USER_PROJECT = 'user-project-123'
        connection = _Connection({'name': BLOB_NAME})
        client = _Client(connection)
        bucket = self._make_one(name=NAME, user_project=USER_PROJECT)
        blob = bucket.get_blob(BLOB_NAME, client=client)
        self.assertIs(blob.bucket, bucket)
        self.assertEqual(blob.name, BLOB_NAME)
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], '/b/%s/o/%s' % (NAME, BLOB_NAME))
        self.assertEqual(kw['query_params'], {'userProject': USER_PROJECT})

    def test_get_blob_hit_with_kwargs(self):
        from google.cloud.storage.blob import _get_encryption_headers

        NAME = 'name'
        BLOB_NAME = 'blob-name'
        CHUNK_SIZE = 1024 * 1024
        KEY = b'01234567890123456789012345678901'  # 32 bytes

        connection = _Connection({'name': BLOB_NAME})
        client = _Client(connection)
        bucket = self._make_one(name=NAME)
        blob = bucket.get_blob(
            BLOB_NAME, client=client, encryption_key=KEY, chunk_size=CHUNK_SIZE
        )
        self.assertIs(blob.bucket, bucket)
        self.assertEqual(blob.name, BLOB_NAME)
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], '/b/%s/o/%s' % (NAME, BLOB_NAME))
        self.assertEqual(kw['headers'], _get_encryption_headers(KEY))
        self.assertEqual(blob.chunk_size, CHUNK_SIZE)
        self.assertEqual(blob._encryption_key, KEY)

    def test_list_blobs_defaults(self):
        NAME = 'name'
        connection = _Connection({'items': []})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        iterator = bucket.list_blobs()
        blobs = list(iterator)
        self.assertEqual(blobs, [])
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], '/b/%s/o' % NAME)
        self.assertEqual(kw['query_params'], {'projection': 'noAcl'})

    def test_list_blobs_w_all_arguments_and_user_project(self):
        NAME = 'name'
        USER_PROJECT = 'user-project-123'
        MAX_RESULTS = 10
        PAGE_TOKEN = 'ABCD'
        PREFIX = 'subfolder'
        DELIMITER = '/'
        VERSIONS = True
        PROJECTION = 'full'
        FIELDS = 'items/contentLanguage,nextPageToken'
        EXPECTED = {
            'maxResults': 10,
            'pageToken': PAGE_TOKEN,
            'prefix': PREFIX,
            'delimiter': DELIMITER,
            'versions': VERSIONS,
            'projection': PROJECTION,
            'fields': FIELDS,
            'userProject': USER_PROJECT,
        }
        connection = _Connection({'items': []})
        client = _Client(connection)
        bucket = self._make_one(name=NAME, user_project=USER_PROJECT)
        iterator = bucket.list_blobs(
            max_results=MAX_RESULTS,
            page_token=PAGE_TOKEN,
            prefix=PREFIX,
            delimiter=DELIMITER,
            versions=VERSIONS,
            projection=PROJECTION,
            fields=FIELDS,
            client=client,
        )
        blobs = list(iterator)
        self.assertEqual(blobs, [])
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], '/b/%s/o' % NAME)
        self.assertEqual(kw['query_params'], EXPECTED)

    def test_list_blobs(self):
        NAME = 'name'
        connection = _Connection({'items': []})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        iterator = bucket.list_blobs()
        blobs = list(iterator)
        self.assertEqual(blobs, [])
        kw, = connection._requested
        self.assertEqual(kw['method'], 'GET')
        self.assertEqual(kw['path'], '/b/%s/o' % NAME)
        self.assertEqual(kw['query_params'], {'projection': 'noAcl'})

    def test_list_notifications(self):
        from google.cloud.storage.notification import BucketNotification
        from google.cloud.storage.notification import _TOPIC_REF_FMT
        from google.cloud.storage.notification import (
            JSON_API_V1_PAYLOAD_FORMAT, NONE_PAYLOAD_FORMAT)

        NAME = 'name'

        topic_refs = [
            ('my-project-123', 'topic-1'),
            ('other-project-456', 'topic-2'),
        ]

        resources = [{
            'topic': _TOPIC_REF_FMT.format(*topic_refs[0]),
            'id': '1',
            'etag': 'DEADBEEF',
            'selfLink': 'https://example.com/notification/1',
            'payload_format': NONE_PAYLOAD_FORMAT,
        }, {
            'topic': _TOPIC_REF_FMT.format(*topic_refs[1]),
            'id': '2',
            'etag': 'FACECABB',
            'selfLink': 'https://example.com/notification/2',
            'payload_format': JSON_API_V1_PAYLOAD_FORMAT,
        }]
        connection = _Connection({'items': resources})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)

        notifications = list(bucket.list_notifications())

        self.assertEqual(len(notifications), len(resources))
        for notification, resource, topic_ref in zip(
                notifications, resources, topic_refs):
            self.assertIsInstance(notification, BucketNotification)
            self.assertEqual(notification.topic_project, topic_ref[0])
            self.assertEqual(notification.topic_name, topic_ref[1])
            self.assertEqual(notification.notification_id, resource['id'])
            self.assertEqual(notification.etag, resource['etag'])
            self.assertEqual(notification.self_link, resource['selfLink'])
            self.assertEqual(
                notification.custom_attributes,
                resource.get('custom_attributes'))
            self.assertEqual(
                notification.event_types, resource.get('event_types'))
            self.assertEqual(
                notification.blob_name_prefix,
                resource.get('blob_name_prefix'))
            self.assertEqual(
                notification.payload_format, resource.get('payload_format'))

    def test_delete_miss(self):
        from google.cloud.exceptions import NotFound

        NAME = 'name'
        connection = _Connection()
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        self.assertRaises(NotFound, bucket.delete)
        expected_cw = [{
            'method': 'DELETE',
            'path': bucket.path,
            'query_params': {},
            '_target_object': None,
        }]
        self.assertEqual(connection._deleted_buckets, expected_cw)

    def test_delete_hit_with_user_project(self):
        NAME = 'name'
        USER_PROJECT = 'user-project-123'
        GET_BLOBS_RESP = {'items': []}
        connection = _Connection(GET_BLOBS_RESP)
        connection._delete_bucket = True
        client = _Client(connection)
        bucket = self._make_one(
            client=client, name=NAME, user_project=USER_PROJECT)
        result = bucket.delete(force=True)
        self.assertIsNone(result)
        expected_cw = [{
            'method': 'DELETE',
            'path': bucket.path,
            '_target_object': None,
            'query_params': {'userProject': USER_PROJECT},
        }]
        self.assertEqual(connection._deleted_buckets, expected_cw)

    def test_delete_force_delete_blobs(self):
        NAME = 'name'
        BLOB_NAME1 = 'blob-name1'
        BLOB_NAME2 = 'blob-name2'
        GET_BLOBS_RESP = {
            'items': [
                {'name': BLOB_NAME1},
                {'name': BLOB_NAME2},
            ],
        }
        DELETE_BLOB1_RESP = DELETE_BLOB2_RESP = {}
        connection = _Connection(GET_BLOBS_RESP, DELETE_BLOB1_RESP,
                                 DELETE_BLOB2_RESP)
        connection._delete_bucket = True
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        result = bucket.delete(force=True)
        self.assertIsNone(result)
        expected_cw = [{
            'method': 'DELETE',
            'path': bucket.path,
            'query_params': {},
            '_target_object': None,
        }]
        self.assertEqual(connection._deleted_buckets, expected_cw)

    def test_delete_force_miss_blobs(self):
        NAME = 'name'
        BLOB_NAME = 'blob-name1'
        GET_BLOBS_RESP = {'items': [{'name': BLOB_NAME}]}
        # Note the connection does not have a response for the blob.
        connection = _Connection(GET_BLOBS_RESP)
        connection._delete_bucket = True
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        result = bucket.delete(force=True)
        self.assertIsNone(result)
        expected_cw = [{
            'method': 'DELETE',
            'path': bucket.path,
            'query_params': {},
            '_target_object': None,
        }]
        self.assertEqual(connection._deleted_buckets, expected_cw)

    def test_delete_too_many(self):
        NAME = 'name'
        BLOB_NAME1 = 'blob-name1'
        BLOB_NAME2 = 'blob-name2'
        GET_BLOBS_RESP = {
            'items': [
                {'name': BLOB_NAME1},
                {'name': BLOB_NAME2},
            ],
        }
        connection = _Connection(GET_BLOBS_RESP)
        connection._delete_bucket = True
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)

        # Make the Bucket refuse to delete with 2 objects.
        bucket._MAX_OBJECTS_FOR_ITERATION = 1
        self.assertRaises(ValueError, bucket.delete, force=True)
        self.assertEqual(connection._deleted_buckets, [])

    def test_delete_blob_miss(self):
        from google.cloud.exceptions import NotFound

        NAME = 'name'
        NONESUCH = 'nonesuch'
        connection = _Connection()
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        self.assertRaises(NotFound, bucket.delete_blob, NONESUCH)
        kw, = connection._requested
        self.assertEqual(kw['method'], 'DELETE')
        self.assertEqual(kw['path'], '/b/%s/o/%s' % (NAME, NONESUCH))
        self.assertEqual(kw['query_params'], {})

    def test_delete_blob_hit_with_user_project(self):
        NAME = 'name'
        BLOB_NAME = 'blob-name'
        USER_PROJECT = 'user-project-123'
        connection = _Connection({})
        client = _Client(connection)
        bucket = self._make_one(
            client=client, name=NAME, user_project=USER_PROJECT)
        result = bucket.delete_blob(BLOB_NAME)
        self.assertIsNone(result)
        kw, = connection._requested
        self.assertEqual(kw['method'], 'DELETE')
        self.assertEqual(kw['path'], '/b/%s/o/%s' % (NAME, BLOB_NAME))
        self.assertEqual(kw['query_params'], {'userProject': USER_PROJECT})

    def test_delete_blobs_empty(self):
        NAME = 'name'
        connection = _Connection()
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.delete_blobs([])
        self.assertEqual(connection._requested, [])

    def test_delete_blobs_hit_w_user_project(self):
        NAME = 'name'
        BLOB_NAME = 'blob-name'
        USER_PROJECT = 'user-project-123'
        connection = _Connection({})
        client = _Client(connection)
        bucket = self._make_one(
            client=client, name=NAME, user_project=USER_PROJECT)
        bucket.delete_blobs([BLOB_NAME])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'DELETE')
        self.assertEqual(kw[0]['path'], '/b/%s/o/%s' % (NAME, BLOB_NAME))
        self.assertEqual(kw[0]['query_params'], {'userProject': USER_PROJECT})

    def test_delete_blobs_miss_no_on_error(self):
        from google.cloud.exceptions import NotFound

        NAME = 'name'
        BLOB_NAME = 'blob-name'
        NONESUCH = 'nonesuch'
        connection = _Connection({})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        self.assertRaises(NotFound, bucket.delete_blobs, [BLOB_NAME, NONESUCH])
        kw = connection._requested
        self.assertEqual(len(kw), 2)
        self.assertEqual(kw[0]['method'], 'DELETE')
        self.assertEqual(kw[0]['path'], '/b/%s/o/%s' % (NAME, BLOB_NAME))
        self.assertEqual(kw[1]['method'], 'DELETE')
        self.assertEqual(kw[1]['path'], '/b/%s/o/%s' % (NAME, NONESUCH))

    def test_delete_blobs_miss_w_on_error(self):
        NAME = 'name'
        BLOB_NAME = 'blob-name'
        NONESUCH = 'nonesuch'
        connection = _Connection({})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        errors = []
        bucket.delete_blobs([BLOB_NAME, NONESUCH], errors.append)
        self.assertEqual(errors, [NONESUCH])
        kw = connection._requested
        self.assertEqual(len(kw), 2)
        self.assertEqual(kw[0]['method'], 'DELETE')
        self.assertEqual(kw[0]['path'], '/b/%s/o/%s' % (NAME, BLOB_NAME))
        self.assertEqual(kw[1]['method'], 'DELETE')
        self.assertEqual(kw[1]['path'], '/b/%s/o/%s' % (NAME, NONESUCH))

    def test_copy_blobs_wo_name(self):
        SOURCE = 'source'
        DEST = 'dest'
        BLOB_NAME = 'blob-name'

        class _Blob(object):
            name = BLOB_NAME
            path = '/b/%s/o/%s' % (SOURCE, BLOB_NAME)

        connection = _Connection({})
        client = _Client(connection)
        source = self._make_one(client=client, name=SOURCE)
        dest = self._make_one(client=client, name=DEST)
        blob = _Blob()
        new_blob = source.copy_blob(blob, dest)
        self.assertIs(new_blob.bucket, dest)
        self.assertEqual(new_blob.name, BLOB_NAME)
        kw, = connection._requested
        COPY_PATH = '/b/%s/o/%s/copyTo/b/%s/o/%s' % (SOURCE, BLOB_NAME,
                                                     DEST, BLOB_NAME)
        self.assertEqual(kw['method'], 'POST')
        self.assertEqual(kw['path'], COPY_PATH)
        self.assertEqual(kw['query_params'], {})

    def test_copy_blobs_source_generation(self):
        SOURCE = 'source'
        DEST = 'dest'
        BLOB_NAME = 'blob-name'
        GENERATION = 1512565576797178

        class _Blob(object):
            name = BLOB_NAME
            path = '/b/%s/o/%s' % (SOURCE, BLOB_NAME)

        connection = _Connection({})
        client = _Client(connection)
        source = self._make_one(client=client, name=SOURCE)
        dest = self._make_one(client=client, name=DEST)
        blob = _Blob()
        new_blob = source.copy_blob(blob, dest, source_generation=GENERATION)
        self.assertIs(new_blob.bucket, dest)
        self.assertEqual(new_blob.name, BLOB_NAME)
        kw, = connection._requested
        COPY_PATH = '/b/%s/o/%s/copyTo/b/%s/o/%s' % (SOURCE, BLOB_NAME,
                                                     DEST, BLOB_NAME)
        self.assertEqual(kw['method'], 'POST')
        self.assertEqual(kw['path'], COPY_PATH)
        self.assertEqual(kw['query_params'], {'sourceGeneration': GENERATION})

    def test_copy_blobs_preserve_acl(self):
        from google.cloud.storage.acl import ObjectACL

        SOURCE = 'source'
        DEST = 'dest'
        BLOB_NAME = 'blob-name'
        NEW_NAME = 'new_name'
        BLOB_PATH = '/b/%s/o/%s' % (SOURCE, BLOB_NAME)
        NEW_BLOB_PATH = '/b/%s/o/%s' % (DEST, NEW_NAME)
        COPY_PATH = '/b/%s/o/%s/copyTo/b/%s/o/%s' % (SOURCE, BLOB_NAME,
                                                     DEST, NEW_NAME)

        class _Blob(object):
            name = BLOB_NAME
            path = BLOB_PATH

        connection = _Connection({}, {})
        client = _Client(connection)
        source = self._make_one(client=client, name=SOURCE)
        dest = self._make_one(client=client, name=DEST)
        blob = _Blob()
        new_blob = source.copy_blob(blob, dest, NEW_NAME, client=client,
                                    preserve_acl=False)
        self.assertIs(new_blob.bucket, dest)
        self.assertEqual(new_blob.name, NEW_NAME)
        self.assertIsInstance(new_blob.acl, ObjectACL)
        kw = connection._requested
        self.assertEqual(len(kw), 2)
        self.assertEqual(kw[0]['method'], 'POST')
        self.assertEqual(kw[0]['path'], COPY_PATH)
        self.assertEqual(kw[0]['query_params'], {})
        self.assertEqual(kw[1]['method'], 'PATCH')
        self.assertEqual(kw[1]['path'], NEW_BLOB_PATH)
        self.assertEqual(kw[1]['query_params'], {'projection': 'full'})

    def test_copy_blobs_w_name_and_user_project(self):
        SOURCE = 'source'
        DEST = 'dest'
        BLOB_NAME = 'blob-name'
        NEW_NAME = 'new_name'
        USER_PROJECT = 'user-project-123'

        class _Blob(object):
            name = BLOB_NAME
            path = '/b/%s/o/%s' % (SOURCE, BLOB_NAME)

        connection = _Connection({})
        client = _Client(connection)
        source = self._make_one(
            client=client, name=SOURCE, user_project=USER_PROJECT)
        dest = self._make_one(client=client, name=DEST)
        blob = _Blob()
        new_blob = source.copy_blob(blob, dest, NEW_NAME)
        self.assertIs(new_blob.bucket, dest)
        self.assertEqual(new_blob.name, NEW_NAME)
        kw, = connection._requested
        COPY_PATH = '/b/%s/o/%s/copyTo/b/%s/o/%s' % (SOURCE, BLOB_NAME,
                                                     DEST, NEW_NAME)
        self.assertEqual(kw['method'], 'POST')
        self.assertEqual(kw['path'], COPY_PATH)
        self.assertEqual(kw['query_params'], {'userProject': USER_PROJECT})

    def test_rename_blob(self):
        BUCKET_NAME = 'BUCKET_NAME'
        BLOB_NAME = 'blob-name'
        NEW_BLOB_NAME = 'new-blob-name'

        DATA = {'name': NEW_BLOB_NAME}
        connection = _Connection(DATA)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=BUCKET_NAME)

        class _Blob(object):

            def __init__(self, name, bucket_name):
                self.name = name
                self.path = '/b/%s/o/%s' % (bucket_name, name)
                self._deleted = []

            def delete(self, client=None):
                self._deleted.append(client)

        blob = _Blob(BLOB_NAME, BUCKET_NAME)
        renamed_blob = bucket.rename_blob(blob, NEW_BLOB_NAME, client=client)
        self.assertIs(renamed_blob.bucket, bucket)
        self.assertEqual(renamed_blob.name, NEW_BLOB_NAME)
        self.assertEqual(blob._deleted, [client])

    def test_etag(self):
        ETAG = 'ETAG'
        properties = {'etag': ETAG}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.etag, ETAG)

    def test_id(self):
        ID = 'ID'
        properties = {'id': ID}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.id, ID)

    def test_location_getter(self):
        NAME = 'name'
        before = {'location': 'AS'}
        bucket = self._make_one(name=NAME, properties=before)
        self.assertEqual(bucket.location, 'AS')

    def test_location_setter(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        self.assertIsNone(bucket.location)
        bucket.location = 'AS'
        self.assertEqual(bucket.location, 'AS')
        self.assertTrue('location' in bucket._changes)

    def test_lifecycle_rules_getter(self):
        NAME = 'name'
        LC_RULE = {'action': {'type': 'Delete'}, 'condition': {'age': 42}}
        rules = [LC_RULE]
        properties = {'lifecycle': {'rule': rules}}
        bucket = self._make_one(name=NAME, properties=properties)
        self.assertEqual(bucket.lifecycle_rules, rules)
        # Make sure it's a copy
        self.assertIsNot(bucket.lifecycle_rules, rules)

    def test_lifecycle_rules_setter(self):
        NAME = 'name'
        LC_RULE = {'action': {'type': 'Delete'}, 'condition': {'age': 42}}
        rules = [LC_RULE]
        bucket = self._make_one(name=NAME)
        self.assertEqual(bucket.lifecycle_rules, [])
        bucket.lifecycle_rules = rules
        self.assertEqual(bucket.lifecycle_rules, rules)
        self.assertTrue('lifecycle' in bucket._changes)

    def test_cors_getter(self):
        NAME = 'name'
        CORS_ENTRY = {
            'maxAgeSeconds': 1234,
            'method': ['OPTIONS', 'GET'],
            'origin': ['127.0.0.1'],
            'responseHeader': ['Content-Type'],
        }
        properties = {'cors': [CORS_ENTRY, {}]}
        bucket = self._make_one(name=NAME, properties=properties)
        entries = bucket.cors
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0], CORS_ENTRY)
        self.assertEqual(entries[1], {})
        # Make sure it was a copy, not the same object.
        self.assertIsNot(entries[0], CORS_ENTRY)

    def test_cors_setter(self):
        NAME = 'name'
        CORS_ENTRY = {
            'maxAgeSeconds': 1234,
            'method': ['OPTIONS', 'GET'],
            'origin': ['127.0.0.1'],
            'responseHeader': ['Content-Type'],
        }
        bucket = self._make_one(name=NAME)

        self.assertEqual(bucket.cors, [])
        bucket.cors = [CORS_ENTRY]
        self.assertEqual(bucket.cors, [CORS_ENTRY])
        self.assertTrue('cors' in bucket._changes)

    def test_default_kms_key_name_getter(self):
        NAME = 'name'
        KMS_RESOURCE = (
            'projects/test-project-123/'
            'locations/us/'
            'keyRings/test-ring/'
            'cryptoKeys/test-key'
        )
        ENCRYPTION_CONFIG = {
            'defaultKmsKeyName': KMS_RESOURCE,
        }
        bucket = self._make_one(name=NAME)
        self.assertIsNone(bucket.default_kms_key_name)
        bucket._properties['encryption'] = ENCRYPTION_CONFIG
        self.assertEqual(bucket.default_kms_key_name, KMS_RESOURCE)

    def test_default_kms_key_name_setter(self):
        NAME = 'name'
        KMS_RESOURCE = (
            'projects/test-project-123/'
            'locations/us/'
            'keyRings/test-ring/'
            'cryptoKeys/test-key'
        )
        ENCRYPTION_CONFIG = {
            'defaultKmsKeyName': KMS_RESOURCE,
        }
        bucket = self._make_one(name=NAME)
        bucket.default_kms_key_name = KMS_RESOURCE
        self.assertEqual(
            bucket._properties['encryption'], ENCRYPTION_CONFIG)
        self.assertTrue('encryption' in bucket._changes)

    def test_labels_getter(self):
        NAME = 'name'
        LABELS = {'color': 'red', 'flavor': 'cherry'}
        properties = {'labels': LABELS}
        bucket = self._make_one(name=NAME, properties=properties)
        labels = bucket.labels
        self.assertEqual(labels, LABELS)
        # Make sure it was a copy, not the same object.
        self.assertIsNot(labels, LABELS)

    def test_labels_setter(self):
        NAME = 'name'
        LABELS = {'color': 'red', 'flavor': 'cherry'}
        bucket = self._make_one(name=NAME)

        self.assertEqual(bucket.labels, {})
        bucket.labels = LABELS
        self.assertEqual(bucket.labels, LABELS)
        self.assertIsNot(bucket._properties['labels'], LABELS)
        self.assertIn('labels', bucket._changes)

    def test_labels_setter_with_removal(self):
        # Make sure the bucket labels look correct and follow the expected
        # public structure.
        bucket = self._make_one(name='name')
        self.assertEqual(bucket.labels, {})
        bucket.labels = {'color': 'red', 'flavor': 'cherry'}
        self.assertEqual(bucket.labels, {'color': 'red', 'flavor': 'cherry'})
        bucket.labels = {'color': 'red'}
        self.assertEqual(bucket.labels, {'color': 'red'})

        # Make sure that a patch call correctly removes the flavor label.
        client = mock.NonCallableMock(spec=('_connection',))
        client._connection = mock.NonCallableMock(spec=('api_request',))
        bucket.patch(client=client)
        client._connection.api_request.assert_called()
        _, _, kwargs = client._connection.api_request.mock_calls[0]
        self.assertEqual(len(kwargs['data']['labels']), 2)
        self.assertEqual(kwargs['data']['labels']['color'], 'red')
        self.assertIsNone(kwargs['data']['labels']['flavor'])

        # A second patch call should be a no-op for labels.
        client._connection.api_request.reset_mock()
        bucket.patch(client=client)
        client._connection.api_request.assert_called()
        _, _, kwargs = client._connection.api_request.mock_calls[0]
        self.assertNotIn('labels', kwargs['data'])

    def test_get_logging_w_prefix(self):
        NAME = 'name'
        LOG_BUCKET = 'logs'
        LOG_PREFIX = 'pfx'
        before = {
            'logging': {
                'logBucket': LOG_BUCKET,
                'logObjectPrefix': LOG_PREFIX,
            },
        }
        bucket = self._make_one(name=NAME, properties=before)
        info = bucket.get_logging()
        self.assertEqual(info['logBucket'], LOG_BUCKET)
        self.assertEqual(info['logObjectPrefix'], LOG_PREFIX)

    def test_enable_logging_defaults(self):
        NAME = 'name'
        LOG_BUCKET = 'logs'
        before = {'logging': None}
        bucket = self._make_one(name=NAME, properties=before)
        self.assertIsNone(bucket.get_logging())
        bucket.enable_logging(LOG_BUCKET)
        info = bucket.get_logging()
        self.assertEqual(info['logBucket'], LOG_BUCKET)
        self.assertEqual(info['logObjectPrefix'], '')

    def test_enable_logging(self):
        NAME = 'name'
        LOG_BUCKET = 'logs'
        LOG_PFX = 'pfx'
        before = {'logging': None}
        bucket = self._make_one(name=NAME, properties=before)
        self.assertIsNone(bucket.get_logging())
        bucket.enable_logging(LOG_BUCKET, LOG_PFX)
        info = bucket.get_logging()
        self.assertEqual(info['logBucket'], LOG_BUCKET)
        self.assertEqual(info['logObjectPrefix'], LOG_PFX)

    def test_disable_logging(self):
        NAME = 'name'
        before = {'logging': {'logBucket': 'logs', 'logObjectPrefix': 'pfx'}}
        bucket = self._make_one(name=NAME, properties=before)
        self.assertIsNotNone(bucket.get_logging())
        bucket.disable_logging()
        self.assertIsNone(bucket.get_logging())

    def test_metageneration(self):
        METAGENERATION = 42
        properties = {'metageneration': METAGENERATION}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.metageneration, METAGENERATION)

    def test_metageneration_unset(self):
        bucket = self._make_one()
        self.assertIsNone(bucket.metageneration)

    def test_metageneration_string_val(self):
        METAGENERATION = 42
        properties = {'metageneration': str(METAGENERATION)}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.metageneration, METAGENERATION)

    def test_owner(self):
        OWNER = {'entity': 'project-owner-12345', 'entityId': '23456'}
        properties = {'owner': OWNER}
        bucket = self._make_one(properties=properties)
        owner = bucket.owner
        self.assertEqual(owner['entity'], 'project-owner-12345')
        self.assertEqual(owner['entityId'], '23456')

    def test_project_number(self):
        PROJECT_NUMBER = 12345
        properties = {'projectNumber': PROJECT_NUMBER}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.project_number, PROJECT_NUMBER)

    def test_project_number_unset(self):
        bucket = self._make_one()
        self.assertIsNone(bucket.project_number)

    def test_project_number_string_val(self):
        PROJECT_NUMBER = 12345
        properties = {'projectNumber': str(PROJECT_NUMBER)}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.project_number, PROJECT_NUMBER)

    def test_self_link(self):
        SELF_LINK = 'http://example.com/self/'
        properties = {'selfLink': SELF_LINK}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.self_link, SELF_LINK)

    def test_storage_class_getter(self):
        STORAGE_CLASS = 'http://example.com/self/'
        properties = {'storageClass': STORAGE_CLASS}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.storage_class, STORAGE_CLASS)

    def test_storage_class_setter_invalid(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        with self.assertRaises(ValueError):
            bucket.storage_class = 'BOGUS'
        self.assertFalse('storageClass' in bucket._changes)

    def test_storage_class_setter_STANDARD(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        bucket.storage_class = 'STANDARD'
        self.assertEqual(bucket.storage_class, 'STANDARD')
        self.assertTrue('storageClass' in bucket._changes)

    def test_storage_class_setter_NEARLINE(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        bucket.storage_class = 'NEARLINE'
        self.assertEqual(bucket.storage_class, 'NEARLINE')
        self.assertTrue('storageClass' in bucket._changes)

    def test_storage_class_setter_COLDLINE(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        bucket.storage_class = 'COLDLINE'
        self.assertEqual(bucket.storage_class, 'COLDLINE')
        self.assertTrue('storageClass' in bucket._changes)

    def test_storage_class_setter_MULTI_REGIONAL(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        bucket.storage_class = 'MULTI_REGIONAL'
        self.assertEqual(bucket.storage_class, 'MULTI_REGIONAL')
        self.assertTrue('storageClass' in bucket._changes)

    def test_storage_class_setter_REGIONAL(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        bucket.storage_class = 'REGIONAL'
        self.assertEqual(bucket.storage_class, 'REGIONAL')
        self.assertTrue('storageClass' in bucket._changes)

    def test_storage_class_setter_DURABLE_REDUCED_AVAILABILITY(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        bucket.storage_class = 'DURABLE_REDUCED_AVAILABILITY'
        self.assertEqual(bucket.storage_class, 'DURABLE_REDUCED_AVAILABILITY')
        self.assertTrue('storageClass' in bucket._changes)

    def test_time_created(self):
        from google.cloud._helpers import _RFC3339_MICROS
        from google.cloud._helpers import UTC

        TIMESTAMP = datetime.datetime(2014, 11, 5, 20, 34, 37, tzinfo=UTC)
        TIME_CREATED = TIMESTAMP.strftime(_RFC3339_MICROS)
        properties = {'timeCreated': TIME_CREATED}
        bucket = self._make_one(properties=properties)
        self.assertEqual(bucket.time_created, TIMESTAMP)

    def test_time_created_unset(self):
        bucket = self._make_one()
        self.assertIsNone(bucket.time_created)

    def test_versioning_enabled_getter_missing(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        self.assertEqual(bucket.versioning_enabled, False)

    def test_versioning_enabled_getter(self):
        NAME = 'name'
        before = {'versioning': {'enabled': True}}
        bucket = self._make_one(name=NAME, properties=before)
        self.assertEqual(bucket.versioning_enabled, True)

    def test_versioning_enabled_setter(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        self.assertFalse(bucket.versioning_enabled)
        bucket.versioning_enabled = True
        self.assertTrue(bucket.versioning_enabled)

    def test_requester_pays_getter_missing(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        self.assertEqual(bucket.requester_pays, False)

    def test_requester_pays_getter(self):
        NAME = 'name'
        before = {'billing': {'requesterPays': True}}
        bucket = self._make_one(name=NAME, properties=before)
        self.assertEqual(bucket.requester_pays, True)

    def test_requester_pays_setter(self):
        NAME = 'name'
        bucket = self._make_one(name=NAME)
        self.assertFalse(bucket.requester_pays)
        bucket.requester_pays = True
        self.assertTrue(bucket.requester_pays)

    def test_configure_website_defaults(self):
        NAME = 'name'
        UNSET = {'website': {'mainPageSuffix': None,
                             'notFoundPage': None}}
        bucket = self._make_one(name=NAME)
        bucket.configure_website()
        self.assertEqual(bucket._properties, UNSET)

    def test_configure_website(self):
        NAME = 'name'
        WEBSITE_VAL = {'website': {'mainPageSuffix': 'html',
                                   'notFoundPage': '404.html'}}
        bucket = self._make_one(name=NAME)
        bucket.configure_website('html', '404.html')
        self.assertEqual(bucket._properties, WEBSITE_VAL)

    def test_disable_website(self):
        NAME = 'name'
        UNSET = {'website': {'mainPageSuffix': None,
                             'notFoundPage': None}}
        bucket = self._make_one(name=NAME)
        bucket.disable_website()
        self.assertEqual(bucket._properties, UNSET)

    def test_get_iam_policy(self):
        from google.cloud.storage.iam import STORAGE_OWNER_ROLE
        from google.cloud.storage.iam import STORAGE_EDITOR_ROLE
        from google.cloud.storage.iam import STORAGE_VIEWER_ROLE
        from google.cloud.iam import Policy

        NAME = 'name'
        PATH = '/b/%s' % (NAME,)
        ETAG = 'DEADBEEF'
        VERSION = 17
        OWNER1 = 'user:phred@example.com'
        OWNER2 = 'group:cloud-logs@google.com'
        EDITOR1 = 'domain:google.com'
        EDITOR2 = 'user:phred@example.com'
        VIEWER1 = 'serviceAccount:1234-abcdef@service.example.com'
        VIEWER2 = 'user:phred@example.com'
        RETURNED = {
            'resourceId': PATH,
            'etag': ETAG,
            'version': VERSION,
            'bindings': [
                {'role': STORAGE_OWNER_ROLE, 'members': [OWNER1, OWNER2]},
                {'role': STORAGE_EDITOR_ROLE, 'members': [EDITOR1, EDITOR2]},
                {'role': STORAGE_VIEWER_ROLE, 'members': [VIEWER1, VIEWER2]},
            ],
        }
        EXPECTED = {
            binding['role']: set(binding['members'])
            for binding in RETURNED['bindings']}
        connection = _Connection(RETURNED)
        client = _Client(connection, None)
        bucket = self._make_one(client=client, name=NAME)

        policy = bucket.get_iam_policy()

        self.assertIsInstance(policy, Policy)
        self.assertEqual(policy.etag, RETURNED['etag'])
        self.assertEqual(policy.version, RETURNED['version'])
        self.assertEqual(dict(policy), EXPECTED)

        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '%s/iam' % (PATH,))
        self.assertEqual(kw[0]['query_params'], {})

    def test_get_iam_policy_w_user_project(self):
        from google.cloud.iam import Policy

        NAME = 'name'
        USER_PROJECT = 'user-project-123'
        PATH = '/b/%s' % (NAME,)
        ETAG = 'DEADBEEF'
        VERSION = 17
        RETURNED = {
            'resourceId': PATH,
            'etag': ETAG,
            'version': VERSION,
            'bindings': [],
        }
        EXPECTED = {}
        connection = _Connection(RETURNED)
        client = _Client(connection, None)
        bucket = self._make_one(
            client=client, name=NAME, user_project=USER_PROJECT)

        policy = bucket.get_iam_policy()

        self.assertIsInstance(policy, Policy)
        self.assertEqual(policy.etag, RETURNED['etag'])
        self.assertEqual(policy.version, RETURNED['version'])
        self.assertEqual(dict(policy), EXPECTED)

        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '%s/iam' % (PATH,))
        self.assertEqual(kw[0]['query_params'], {'userProject': USER_PROJECT})

    def test_set_iam_policy(self):
        import operator
        from google.cloud.storage.iam import STORAGE_OWNER_ROLE
        from google.cloud.storage.iam import STORAGE_EDITOR_ROLE
        from google.cloud.storage.iam import STORAGE_VIEWER_ROLE
        from google.cloud.iam import Policy

        NAME = 'name'
        PATH = '/b/%s' % (NAME,)
        ETAG = 'DEADBEEF'
        VERSION = 17
        OWNER1 = 'user:phred@example.com'
        OWNER2 = 'group:cloud-logs@google.com'
        EDITOR1 = 'domain:google.com'
        EDITOR2 = 'user:phred@example.com'
        VIEWER1 = 'serviceAccount:1234-abcdef@service.example.com'
        VIEWER2 = 'user:phred@example.com'
        BINDINGS = [
            {'role': STORAGE_OWNER_ROLE, 'members': [OWNER1, OWNER2]},
            {'role': STORAGE_EDITOR_ROLE, 'members': [EDITOR1, EDITOR2]},
            {'role': STORAGE_VIEWER_ROLE, 'members': [VIEWER1, VIEWER2]},
        ]
        RETURNED = {
            'etag': ETAG,
            'version': VERSION,
            'bindings': BINDINGS,
        }
        policy = Policy()
        for binding in BINDINGS:
            policy[binding['role']] = binding['members']

        connection = _Connection(RETURNED)
        client = _Client(connection, None)
        bucket = self._make_one(client=client, name=NAME)

        returned = bucket.set_iam_policy(policy)

        self.assertEqual(returned.etag, ETAG)
        self.assertEqual(returned.version, VERSION)
        self.assertEqual(dict(returned), dict(policy))

        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PUT')
        self.assertEqual(kw[0]['path'], '%s/iam' % (PATH,))
        self.assertEqual(kw[0]['query_params'], {})
        sent = kw[0]['data']
        self.assertEqual(sent['resourceId'], PATH)
        self.assertEqual(len(sent['bindings']), len(BINDINGS))
        key = operator.itemgetter('role')
        for found, expected in zip(
                sorted(sent['bindings'], key=key),
                sorted(BINDINGS, key=key)):
            self.assertEqual(found['role'], expected['role'])
            self.assertEqual(
                sorted(found['members']), sorted(expected['members']))

    def test_set_iam_policy_w_user_project(self):
        import operator
        from google.cloud.storage.iam import STORAGE_OWNER_ROLE
        from google.cloud.storage.iam import STORAGE_EDITOR_ROLE
        from google.cloud.storage.iam import STORAGE_VIEWER_ROLE
        from google.cloud.iam import Policy

        NAME = 'name'
        USER_PROJECT = 'user-project-123'
        PATH = '/b/%s' % (NAME,)
        ETAG = 'DEADBEEF'
        VERSION = 17
        OWNER1 = 'user:phred@example.com'
        OWNER2 = 'group:cloud-logs@google.com'
        EDITOR1 = 'domain:google.com'
        EDITOR2 = 'user:phred@example.com'
        VIEWER1 = 'serviceAccount:1234-abcdef@service.example.com'
        VIEWER2 = 'user:phred@example.com'
        BINDINGS = [
            {'role': STORAGE_OWNER_ROLE, 'members': [OWNER1, OWNER2]},
            {'role': STORAGE_EDITOR_ROLE, 'members': [EDITOR1, EDITOR2]},
            {'role': STORAGE_VIEWER_ROLE, 'members': [VIEWER1, VIEWER2]},
        ]
        RETURNED = {
            'etag': ETAG,
            'version': VERSION,
            'bindings': BINDINGS,
        }
        policy = Policy()
        for binding in BINDINGS:
            policy[binding['role']] = binding['members']

        connection = _Connection(RETURNED)
        client = _Client(connection, None)
        bucket = self._make_one(
            client=client, name=NAME, user_project=USER_PROJECT)

        returned = bucket.set_iam_policy(policy)

        self.assertEqual(returned.etag, ETAG)
        self.assertEqual(returned.version, VERSION)
        self.assertEqual(dict(returned), dict(policy))

        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PUT')
        self.assertEqual(kw[0]['path'], '%s/iam' % (PATH,))
        self.assertEqual(kw[0]['query_params'], {'userProject': USER_PROJECT})
        sent = kw[0]['data']
        self.assertEqual(sent['resourceId'], PATH)
        self.assertEqual(len(sent['bindings']), len(BINDINGS))
        key = operator.itemgetter('role')
        for found, expected in zip(
                sorted(sent['bindings'], key=key),
                sorted(BINDINGS, key=key)):
            self.assertEqual(found['role'], expected['role'])
            self.assertEqual(
                sorted(found['members']), sorted(expected['members']))

    def test_test_iam_permissions(self):
        from google.cloud.storage.iam import STORAGE_OBJECTS_LIST
        from google.cloud.storage.iam import STORAGE_BUCKETS_GET
        from google.cloud.storage.iam import STORAGE_BUCKETS_UPDATE

        NAME = 'name'
        PATH = '/b/%s' % (NAME,)
        PERMISSIONS = [
            STORAGE_OBJECTS_LIST,
            STORAGE_BUCKETS_GET,
            STORAGE_BUCKETS_UPDATE,
        ]
        ALLOWED = PERMISSIONS[1:]
        RETURNED = {'permissions': ALLOWED}
        connection = _Connection(RETURNED)
        client = _Client(connection, None)
        bucket = self._make_one(client=client, name=NAME)

        allowed = bucket.test_iam_permissions(PERMISSIONS)

        self.assertEqual(allowed, ALLOWED)

        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '%s/iam/testPermissions' % (PATH,))
        self.assertEqual(kw[0]['query_params'], {'permissions': PERMISSIONS})

    def test_test_iam_permissions_w_user_project(self):
        from google.cloud.storage.iam import STORAGE_OBJECTS_LIST
        from google.cloud.storage.iam import STORAGE_BUCKETS_GET
        from google.cloud.storage.iam import STORAGE_BUCKETS_UPDATE

        NAME = 'name'
        USER_PROJECT = 'user-project-123'
        PATH = '/b/%s' % (NAME,)
        PERMISSIONS = [
            STORAGE_OBJECTS_LIST,
            STORAGE_BUCKETS_GET,
            STORAGE_BUCKETS_UPDATE,
        ]
        ALLOWED = PERMISSIONS[1:]
        RETURNED = {'permissions': ALLOWED}
        connection = _Connection(RETURNED)
        client = _Client(connection, None)
        bucket = self._make_one(
            client=client, name=NAME, user_project=USER_PROJECT)

        allowed = bucket.test_iam_permissions(PERMISSIONS)

        self.assertEqual(allowed, ALLOWED)

        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '%s/iam/testPermissions' % (PATH,))
        self.assertEqual(
            kw[0]['query_params'],
            {'permissions': PERMISSIONS, 'userProject': USER_PROJECT})

    def test_make_public_defaults(self):
        from google.cloud.storage.acl import _ACLEntity

        NAME = 'name'
        permissive = [{'entity': 'allUsers', 'role': _ACLEntity.READER_ROLE}]
        after = {'acl': permissive, 'defaultObjectAcl': []}
        connection = _Connection(after)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = True
        bucket.make_public()
        self.assertEqual(list(bucket.acl), permissive)
        self.assertEqual(list(bucket.default_object_acl), [])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': after['acl']})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})

    def _make_public_w_future_helper(self, default_object_acl_loaded=True):
        from google.cloud.storage.acl import _ACLEntity

        NAME = 'name'
        permissive = [{'entity': 'allUsers', 'role': _ACLEntity.READER_ROLE}]
        after1 = {'acl': permissive, 'defaultObjectAcl': []}
        after2 = {'acl': permissive, 'defaultObjectAcl': permissive}
        if default_object_acl_loaded:
            num_requests = 2
            connection = _Connection(after1, after2)
        else:
            num_requests = 3
            # We return the same value for default_object_acl.reload()
            # to consume.
            connection = _Connection(after1, after1, after2)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = default_object_acl_loaded
        bucket.make_public(future=True)
        self.assertEqual(list(bucket.acl), permissive)
        self.assertEqual(list(bucket.default_object_acl), permissive)
        kw = connection._requested
        self.assertEqual(len(kw), num_requests)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': permissive})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})
        if not default_object_acl_loaded:
            self.assertEqual(kw[1]['method'], 'GET')
            self.assertEqual(kw[1]['path'], '/b/%s/defaultObjectAcl' % NAME)
        # Last could be 1 or 2 depending on `default_object_acl_loaded`.
        self.assertEqual(kw[-1]['method'], 'PATCH')
        self.assertEqual(kw[-1]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[-1]['data'], {'defaultObjectAcl': permissive})
        self.assertEqual(kw[-1]['query_params'], {'projection': 'full'})

    def test_make_public_w_future(self):
        self._make_public_w_future_helper(default_object_acl_loaded=True)

    def test_make_public_w_future_reload_default(self):
        self._make_public_w_future_helper(default_object_acl_loaded=False)

    def test_make_public_recursive(self):
        from google.cloud.storage.acl import _ACLEntity

        _saved = []

        class _Blob(object):
            _granted = False

            def __init__(self, bucket, name):
                self._bucket = bucket
                self._name = name

            @property
            def acl(self):
                return self

            # Faux ACL methods
            def all(self):
                return self

            def grant_read(self):
                self._granted = True

            def save(self, client=None):
                _saved.append(
                    (self._bucket, self._name, self._granted, client))

        def item_to_blob(self, item):
            return _Blob(self.bucket, item['name'])

        NAME = 'name'
        BLOB_NAME = 'blob-name'
        permissive = [{'entity': 'allUsers', 'role': _ACLEntity.READER_ROLE}]
        after = {'acl': permissive, 'defaultObjectAcl': []}
        connection = _Connection(after, {'items': [{'name': BLOB_NAME}]})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = True

        with mock.patch('google.cloud.storage.bucket._item_to_blob',
                        new=item_to_blob):
            bucket.make_public(recursive=True)
        self.assertEqual(list(bucket.acl), permissive)
        self.assertEqual(list(bucket.default_object_acl), [])
        self.assertEqual(_saved, [(bucket, BLOB_NAME, True, None)])
        kw = connection._requested
        self.assertEqual(len(kw), 2)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': permissive})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})
        self.assertEqual(kw[1]['method'], 'GET')
        self.assertEqual(kw[1]['path'], '/b/%s/o' % NAME)
        max_results = bucket._MAX_OBJECTS_FOR_ITERATION + 1
        self.assertEqual(kw[1]['query_params'],
                         {'maxResults': max_results, 'projection': 'full'})

    def test_make_public_recursive_too_many(self):
        from google.cloud.storage.acl import _ACLEntity

        PERMISSIVE = [{'entity': 'allUsers', 'role': _ACLEntity.READER_ROLE}]
        AFTER = {'acl': PERMISSIVE, 'defaultObjectAcl': []}

        NAME = 'name'
        BLOB_NAME1 = 'blob-name1'
        BLOB_NAME2 = 'blob-name2'
        GET_BLOBS_RESP = {
            'items': [
                {'name': BLOB_NAME1},
                {'name': BLOB_NAME2},
            ],
        }
        connection = _Connection(AFTER, GET_BLOBS_RESP)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = True

        # Make the Bucket refuse to make_public with 2 objects.
        bucket._MAX_OBJECTS_FOR_ITERATION = 1
        self.assertRaises(ValueError, bucket.make_public, recursive=True)

    def test_make_private_defaults(self):
        NAME = 'name'
        no_permissions = []
        after = {'acl': no_permissions, 'defaultObjectAcl': []}
        connection = _Connection(after)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = True
        bucket.make_private()
        self.assertEqual(list(bucket.acl), no_permissions)
        self.assertEqual(list(bucket.default_object_acl), [])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': after['acl']})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})

    def _make_private_w_future_helper(self, default_object_acl_loaded=True):
        NAME = 'name'
        no_permissions = []
        after1 = {'acl': no_permissions, 'defaultObjectAcl': []}
        after2 = {'acl': no_permissions, 'defaultObjectAcl': no_permissions}
        if default_object_acl_loaded:
            num_requests = 2
            connection = _Connection(after1, after2)
        else:
            num_requests = 3
            # We return the same value for default_object_acl.reload()
            # to consume.
            connection = _Connection(after1, after1, after2)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = default_object_acl_loaded
        bucket.make_private(future=True)
        self.assertEqual(list(bucket.acl), no_permissions)
        self.assertEqual(list(bucket.default_object_acl), no_permissions)
        kw = connection._requested
        self.assertEqual(len(kw), num_requests)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': no_permissions})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})
        if not default_object_acl_loaded:
            self.assertEqual(kw[1]['method'], 'GET')
            self.assertEqual(kw[1]['path'], '/b/%s/defaultObjectAcl' % NAME)
        # Last could be 1 or 2 depending on `default_object_acl_loaded`.
        self.assertEqual(kw[-1]['method'], 'PATCH')
        self.assertEqual(kw[-1]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[-1]['data'], {'defaultObjectAcl': no_permissions})
        self.assertEqual(kw[-1]['query_params'], {'projection': 'full'})

    def test_make_private_w_future(self):
        self._make_private_w_future_helper(default_object_acl_loaded=True)

    def test_make_private_w_future_reload_default(self):
        self._make_private_w_future_helper(default_object_acl_loaded=False)

    def test_make_private_recursive(self):
        _saved = []

        class _Blob(object):
            _granted = True

            def __init__(self, bucket, name):
                self._bucket = bucket
                self._name = name

            @property
            def acl(self):
                return self

            # Faux ACL methods
            def all(self):
                return self

            def revoke_read(self):
                self._granted = False

            def save(self, client=None):
                _saved.append(
                    (self._bucket, self._name, self._granted, client))

        def item_to_blob(self, item):
            return _Blob(self.bucket, item['name'])

        NAME = 'name'
        BLOB_NAME = 'blob-name'
        no_permissions = []
        after = {'acl': no_permissions, 'defaultObjectAcl': []}
        connection = _Connection(after, {'items': [{'name': BLOB_NAME}]})
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = True

        with mock.patch('google.cloud.storage.bucket._item_to_blob',
                        new=item_to_blob):
            bucket.make_private(recursive=True)
        self.assertEqual(list(bucket.acl), no_permissions)
        self.assertEqual(list(bucket.default_object_acl), [])
        self.assertEqual(_saved, [(bucket, BLOB_NAME, False, None)])
        kw = connection._requested
        self.assertEqual(len(kw), 2)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': no_permissions})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})
        self.assertEqual(kw[1]['method'], 'GET')
        self.assertEqual(kw[1]['path'], '/b/%s/o' % NAME)
        max_results = bucket._MAX_OBJECTS_FOR_ITERATION + 1
        self.assertEqual(kw[1]['query_params'],
                         {'maxResults': max_results, 'projection': 'full'})

    def test_make_private_recursive_too_many(self):
        NO_PERMISSIONS = []
        AFTER = {'acl': NO_PERMISSIONS, 'defaultObjectAcl': []}

        NAME = 'name'
        BLOB_NAME1 = 'blob-name1'
        BLOB_NAME2 = 'blob-name2'
        GET_BLOBS_RESP = {
            'items': [
                {'name': BLOB_NAME1},
                {'name': BLOB_NAME2},
            ],
        }
        connection = _Connection(AFTER, GET_BLOBS_RESP)
        client = _Client(connection)
        bucket = self._make_one(client=client, name=NAME)
        bucket.acl.loaded = True
        bucket.default_object_acl.loaded = True

        # Make the Bucket refuse to make_private with 2 objects.
        bucket._MAX_OBJECTS_FOR_ITERATION = 1
        self.assertRaises(ValueError, bucket.make_private, recursive=True)

    def test_page_empty_response(self):
        from google.api_core import page_iterator

        connection = _Connection()
        client = _Client(connection)
        name = 'name'
        bucket = self._make_one(client=client, name=name)
        iterator = bucket.list_blobs()
        page = page_iterator.Page(iterator, (), None)
        iterator._page = page
        blobs = list(page)
        self.assertEqual(blobs, [])
        self.assertEqual(iterator.prefixes, set())

    def test_page_non_empty_response(self):
        import six
        from google.cloud.storage.blob import Blob

        blob_name = 'blob-name'
        response = {'items': [{'name': blob_name}], 'prefixes': ['foo']}
        connection = _Connection()
        client = _Client(connection)
        name = 'name'
        bucket = self._make_one(client=client, name=name)

        def dummy_response():
            return response

        iterator = bucket.list_blobs()
        iterator._get_next_page_response = dummy_response

        page = six.next(iterator.pages)
        self.assertEqual(page.prefixes, ('foo',))
        self.assertEqual(page.num_items, 1)
        blob = six.next(page)
        self.assertEqual(page.remaining, 0)
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.name, blob_name)
        self.assertEqual(iterator.prefixes, set(['foo']))

    def test_cumulative_prefixes(self):
        import six
        from google.cloud.storage.blob import Blob

        BLOB_NAME = 'blob-name1'
        response1 = {
            'items': [{'name': BLOB_NAME}],
            'prefixes': ['foo'],
            'nextPageToken': 's39rmf9',
        }
        response2 = {
            'items': [],
            'prefixes': ['bar'],
        }
        connection = _Connection()
        client = _Client(connection)
        name = 'name'
        bucket = self._make_one(client=client, name=name)
        responses = [response1, response2]

        def dummy_response():
            return responses.pop(0)

        iterator = bucket.list_blobs()
        iterator._get_next_page_response = dummy_response

        # Parse first response.
        pages_iter = iterator.pages
        page1 = six.next(pages_iter)
        self.assertEqual(page1.prefixes, ('foo',))
        self.assertEqual(page1.num_items, 1)
        blob = six.next(page1)
        self.assertEqual(page1.remaining, 0)
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.name, BLOB_NAME)
        self.assertEqual(iterator.prefixes, set(['foo']))
        # Parse second response.
        page2 = six.next(pages_iter)
        self.assertEqual(page2.prefixes, ('bar',))
        self.assertEqual(page2.num_items, 0)
        self.assertEqual(iterator.prefixes, set(['foo', 'bar']))

    def _test_generate_upload_policy_helper(self, **kwargs):
        import base64
        import json

        credentials = _create_signing_credentials()
        credentials.signer_email = mock.sentinel.signer_email
        credentials.sign_bytes.return_value = b'DEADBEEF'
        connection = _Connection()
        connection.credentials = credentials
        client = _Client(connection)
        name = 'name'
        bucket = self._make_one(client=client, name=name)

        conditions = [
            ['starts-with', '$key', '']]

        policy_fields = bucket.generate_upload_policy(conditions, **kwargs)

        self.assertEqual(policy_fields['bucket'], bucket.name)
        self.assertEqual(
            policy_fields['GoogleAccessId'], mock.sentinel.signer_email)
        self.assertEqual(
            policy_fields['signature'],
            base64.b64encode(b'DEADBEEF').decode('utf-8'))

        policy = json.loads(
            base64.b64decode(policy_fields['policy']).decode('utf-8'))

        policy_conditions = policy['conditions']
        expected_conditions = [{'bucket': bucket.name}] + conditions
        for expected_condition in expected_conditions:
            for condition in policy_conditions:
                if condition == expected_condition:
                    break
            else:  # pragma: NO COVER
                self.fail('Condition {} not found in {}'.format(
                    expected_condition, policy_conditions))

        return policy_fields, policy

    @mock.patch(
        'google.cloud.storage.bucket._NOW',
        return_value=datetime.datetime(1990, 1, 1))
    def test_generate_upload_policy(self, now):
        from google.cloud._helpers import _datetime_to_rfc3339

        _, policy = self._test_generate_upload_policy_helper()

        self.assertEqual(
            policy['expiration'],
            _datetime_to_rfc3339(
                now() + datetime.timedelta(hours=1)))

    def test_generate_upload_policy_args(self):
        from google.cloud._helpers import _datetime_to_rfc3339

        expiration = datetime.datetime(1990, 5, 29)

        _, policy = self._test_generate_upload_policy_helper(
            expiration=expiration)

        self.assertEqual(
            policy['expiration'],
            _datetime_to_rfc3339(expiration))

    def test_generate_upload_policy_bad_credentials(self):
        credentials = object()
        connection = _Connection()
        connection.credentials = credentials
        client = _Client(connection)
        name = 'name'
        bucket = self._make_one(client=client, name=name)

        with self.assertRaises(AttributeError):
            bucket.generate_upload_policy([])


class _Connection(object):
    _delete_bucket = False

    def __init__(self, *responses):
        self._responses = responses
        self._requested = []
        self._deleted_buckets = []
        self.credentials = None

    @staticmethod
    def _is_bucket_path(path):
        # Now just ensure the path only has /b/ and one more segment.
        return path.startswith('/b/') and path.count('/') == 2

    def api_request(self, **kw):
        from google.cloud.exceptions import NotFound

        self._requested.append(kw)

        method = kw.get('method')
        path = kw.get('path', '')
        if method == 'DELETE' and self._is_bucket_path(path):
            self._deleted_buckets.append(kw)
            if self._delete_bucket:
                return
            else:
                raise NotFound('miss')

        try:
            response, self._responses = self._responses[0], self._responses[1:]
        except IndexError:
            raise NotFound('miss')
        else:
            return response


class _Client(object):

    def __init__(self, connection, project=None):
        self._connection = connection
        self._base_connection = connection
        self.project = project
