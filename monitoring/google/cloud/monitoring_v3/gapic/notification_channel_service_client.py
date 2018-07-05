# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Accesses the google.monitoring.v3 NotificationChannelService API."""

import functools
import pkg_resources

import google.api_core.gapic_v1.client_info
import google.api_core.gapic_v1.config
import google.api_core.gapic_v1.method
import google.api_core.grpc_helpers
import google.api_core.page_iterator
import google.api_core.path_template
import grpc

from google.api import metric_pb2 as api_metric_pb2
from google.api import monitored_resource_pb2
from google.cloud.monitoring_v3.gapic import enums
from google.cloud.monitoring_v3.gapic import notification_channel_service_client_config
from google.cloud.monitoring_v3.proto import alert_pb2
from google.cloud.monitoring_v3.proto import alert_service_pb2
from google.cloud.monitoring_v3.proto import alert_service_pb2_grpc
from google.cloud.monitoring_v3.proto import common_pb2
from google.cloud.monitoring_v3.proto import group_pb2
from google.cloud.monitoring_v3.proto import group_service_pb2
from google.cloud.monitoring_v3.proto import group_service_pb2_grpc
from google.cloud.monitoring_v3.proto import metric_pb2 as proto_metric_pb2
from google.cloud.monitoring_v3.proto import metric_service_pb2
from google.cloud.monitoring_v3.proto import metric_service_pb2_grpc
from google.cloud.monitoring_v3.proto import notification_pb2
from google.cloud.monitoring_v3.proto import notification_service_pb2
from google.cloud.monitoring_v3.proto import notification_service_pb2_grpc
from google.protobuf import empty_pb2
from google.protobuf import field_mask_pb2

_GAPIC_LIBRARY_VERSION = pkg_resources.get_distribution(
    'google-cloud-monitoring', ).version


class NotificationChannelServiceClient(object):
    """
    The Notification Channel API provides access to configuration that
    controls how messages related to incidents are sent.
    """

    SERVICE_ADDRESS = 'monitoring.googleapis.com:443'
    """The default address of the service."""

    # The scopes needed to make gRPC calls to all of the methods defined in
    # this service
    _DEFAULT_SCOPES = (
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/monitoring',
        'https://www.googleapis.com/auth/monitoring.read',
        'https://www.googleapis.com/auth/monitoring.write',
    )

    # The name of the interface for this client. This is the key used to find
    # method configuration in the client_config dictionary.
    _INTERFACE_NAME = 'google.monitoring.v3.NotificationChannelService'

    @classmethod
    def project_path(cls, project):
        """Return a fully-qualified project string."""
        return google.api_core.path_template.expand(
            'projects/{project}',
            project=project,
        )

    @classmethod
    def notification_channel_path(cls, project, notification_channel):
        """Return a fully-qualified notification_channel string."""
        return google.api_core.path_template.expand(
            'projects/{project}/notificationChannels/{notification_channel}',
            project=project,
            notification_channel=notification_channel,
        )

    @classmethod
    def notification_channel_descriptor_path(cls, project, channel_descriptor):
        """Return a fully-qualified notification_channel_descriptor string."""
        return google.api_core.path_template.expand(
            'projects/{project}/notificationChannelDescriptors/{channel_descriptor}',
            project=project,
            channel_descriptor=channel_descriptor,
        )

    def __init__(
            self,
            channel=None,
            credentials=None,
            client_config=notification_channel_service_client_config.config,
            client_info=None):
        """Constructor.

        Args:
            channel (grpc.Channel): A ``Channel`` instance through
                which to make calls. This argument is mutually exclusive
                with ``credentials``; providing both will raise an exception.
            credentials (google.auth.credentials.Credentials): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            client_config (dict): A dictionary of call options for each
                method. If not specified, the default configuration is used.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
        """
        # If both `channel` and `credentials` are specified, raise an
        # exception (channels come with credentials baked in already).
        if channel is not None and credentials is not None:
            raise ValueError(
                'The `channel` and `credentials` arguments to {} are mutually '
                'exclusive.'.format(self.__class__.__name__), )

        # Create the channel.
        self.channel = channel
        if self.channel is None:
            self.channel = google.api_core.grpc_helpers.create_channel(
                self.SERVICE_ADDRESS,
                credentials=credentials,
                scopes=self._DEFAULT_SCOPES,
            )

        # Create the gRPC stubs.
        self._notification_channel_service_stub = (
            notification_service_pb2_grpc.NotificationChannelServiceStub(
                self.channel))

        if client_info is None:
            client_info = (
                google.api_core.gapic_v1.client_info.DEFAULT_CLIENT_INFO)
        client_info.gapic_version = _GAPIC_LIBRARY_VERSION
        self._client_info = client_info

        # Parse out the default settings for retry and timeout for each RPC
        # from the client configuration.
        # (Ordinarily, these are the defaults specified in the `*_config.py`
        # file next to this one.)
        self._method_configs = google.api_core.gapic_v1.config.parse_method_configs(
            client_config['interfaces'][self._INTERFACE_NAME], )

        self._inner_api_calls = {}

    def _intercept_channel(self, *interceptors):
        """ Experimental. Bind gRPC interceptors to the gRPC channel.

        Args:
            interceptors (*Union[grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamingClientInterceptor, grpc.StreamingUnaryClientInterceptor, grpc.StreamingStreamingClientInterceptor]):
              Zero or more gRPC interceptors. Interceptors are given control in the order
              they are listed.
        Raises:
            TypeError: If interceptor does not derive from any of
              UnaryUnaryClientInterceptor,
              UnaryStreamClientInterceptor,
              StreamUnaryClientInterceptor, or
              StreamStreamClientInterceptor.
        """
        self.channel = grpc.intercept_channel(self.channel, *interceptors)
        self._notification_channel_service_stub = (
            notification_service_pb2_grpc.NotificationChannelServiceStub(
                self.channel))
        self._inner_api_calls.clear()

    # Service calls
    def list_notification_channel_descriptors(
            self,
            name,
            page_size=None,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Lists the descriptors for supported channel types. The use of descriptors
        makes it possible for new channel types to be dynamically added.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_notification_channel_descriptors(name):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_notification_channel_descriptors(name, options=CallOptions(page_token=INITIAL_PAGE)):
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            name (str): The REST resource name of the parent from which to retrieve
                the notification channel descriptors. The expected syntax is:

                ::

                    projects/[PROJECT_ID]

                Note that this names the parent container in which to look for the
                descriptors; to retrieve a single descriptor by name, use the
                ``GetNotificationChannelDescriptor``
                operation, instead.
            page_size (int): The maximum number of resources contained in the
                underlying API response. If page streaming is performed per-
                resource, this parameter does not affect the return value. If page
                streaming is performed per-page, this determines the maximum number
                of resources in a page.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.gax.PageIterator` instance. By default, this
            is an iterable of :class:`~google.cloud.monitoring_v3.types.NotificationChannelDescriptor` instances.
            This object can also be configured to iterate over the pages
            of the response through the `options` parameter.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'list_notification_channel_descriptors' not in self._inner_api_calls:
            self._inner_api_calls[
                'list_notification_channel_descriptors'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    ListNotificationChannelDescriptors,
                    default_retry=self._method_configs[
                        'ListNotificationChannelDescriptors'].retry,
                    default_timeout=self._method_configs[
                        'ListNotificationChannelDescriptors'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.ListNotificationChannelDescriptorsRequest(
            name=name,
            page_size=page_size,
        )
        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls['list_notification_channel_descriptors'],
                retry=retry,
                timeout=timeout,
                metadata=metadata),
            request=request,
            items_field='channel_descriptors',
            request_token_field='page_token',
            response_token_field='next_page_token',
        )
        return iterator

    def get_notification_channel_descriptor(
            self,
            name,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Gets a single channel descriptor. The descriptor indicates which fields
        are expected / permitted for a notification channel of the given type.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> name = client.notification_channel_descriptor_path('[PROJECT]', '[CHANNEL_DESCRIPTOR]')
            >>>
            >>> response = client.get_notification_channel_descriptor(name)

        Args:
            name (str): The channel type for which to execute the request. The format is
                ``projects/[PROJECT_ID]/notificationChannelDescriptors/{channel_type}``.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.NotificationChannelDescriptor` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'get_notification_channel_descriptor' not in self._inner_api_calls:
            self._inner_api_calls[
                'get_notification_channel_descriptor'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    GetNotificationChannelDescriptor,
                    default_retry=self._method_configs[
                        'GetNotificationChannelDescriptor'].retry,
                    default_timeout=self._method_configs[
                        'GetNotificationChannelDescriptor'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.GetNotificationChannelDescriptorRequest(
            name=name, )
        return self._inner_api_calls['get_notification_channel_descriptor'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def list_notification_channels(
            self,
            name,
            filter_=None,
            order_by=None,
            page_size=None,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Lists the notification channels that have been created for the project.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_notification_channels(name):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_notification_channels(name, options=CallOptions(page_token=INITIAL_PAGE)):
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            name (str): The project on which to execute the request. The format is
                ``projects/[PROJECT_ID]``. That is, this names the container
                in which to look for the notification channels; it does not name a
                specific channel. To query a specific channel by REST resource name, use
                the
                ````GetNotificationChannel```` operation.
            filter_ (str): If provided, this field specifies the criteria that must be met by
                notification channels to be included in the response.

                For more details, see [sorting and
                filtering](/monitoring/api/v3/sorting-and-filtering).
            order_by (str): A comma-separated list of fields by which to sort the result. Supports
                the same set of fields as in ``filter``. Entries can be prefixed with
                a minus sign to sort in descending rather than ascending order.

                For more details, see [sorting and
                filtering](/monitoring/api/v3/sorting-and-filtering).
            page_size (int): The maximum number of resources contained in the
                underlying API response. If page streaming is performed per-
                resource, this parameter does not affect the return value. If page
                streaming is performed per-page, this determines the maximum number
                of resources in a page.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.gax.PageIterator` instance. By default, this
            is an iterable of :class:`~google.cloud.monitoring_v3.types.NotificationChannel` instances.
            This object can also be configured to iterate over the pages
            of the response through the `options` parameter.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'list_notification_channels' not in self._inner_api_calls:
            self._inner_api_calls[
                'list_notification_channels'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    ListNotificationChannels,
                    default_retry=self._method_configs[
                        'ListNotificationChannels'].retry,
                    default_timeout=self._method_configs[
                        'ListNotificationChannels'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.ListNotificationChannelsRequest(
            name=name,
            filter=filter_,
            order_by=order_by,
            page_size=page_size,
        )
        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls['list_notification_channels'],
                retry=retry,
                timeout=timeout,
                metadata=metadata),
            request=request,
            items_field='notification_channels',
            request_token_field='page_token',
            response_token_field='next_page_token',
        )
        return iterator

    def get_notification_channel(
            self,
            name,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Gets a single notification channel. The channel includes the relevant
        configuration details with which the channel was created. However, the
        response may truncate or omit passwords, API keys, or other private key
        matter and thus the response may not be 100% identical to the information
        that was supplied in the call to the create method.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> name = client.notification_channel_path('[PROJECT]', '[NOTIFICATION_CHANNEL]')
            >>>
            >>> response = client.get_notification_channel(name)

        Args:
            name (str): The channel for which to execute the request. The format is
                ``projects/[PROJECT_ID]/notificationChannels/[CHANNEL_ID]``.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.NotificationChannel` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'get_notification_channel' not in self._inner_api_calls:
            self._inner_api_calls[
                'get_notification_channel'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    GetNotificationChannel,
                    default_retry=self._method_configs[
                        'GetNotificationChannel'].retry,
                    default_timeout=self._method_configs[
                        'GetNotificationChannel'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.GetNotificationChannelRequest(
            name=name, )
        return self._inner_api_calls['get_notification_channel'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def create_notification_channel(
            self,
            name,
            notification_channel,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Creates a new notification channel, representing a single notification
        endpoint such as an email address, SMS number, or pagerduty service.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # TODO: Initialize ``notification_channel``:
            >>> notification_channel = {}
            >>>
            >>> response = client.create_notification_channel(name, notification_channel)

        Args:
            name (str): The project on which to execute the request. The format is:

                ::

                    projects/[PROJECT_ID]

                Note that this names the container into which the channel will be
                written. This does not name the newly created channel. The resulting
                channel's name will have a normalized version of this field as a prefix,
                but will add ``/notificationChannels/[CHANNEL_ID]`` to identify the channel.
            notification_channel (Union[dict, ~google.cloud.monitoring_v3.types.NotificationChannel]): The definition of the ``NotificationChannel`` to create.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.NotificationChannel`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.NotificationChannel` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'create_notification_channel' not in self._inner_api_calls:
            self._inner_api_calls[
                'create_notification_channel'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    CreateNotificationChannel,
                    default_retry=self._method_configs[
                        'CreateNotificationChannel'].retry,
                    default_timeout=self._method_configs[
                        'CreateNotificationChannel'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.CreateNotificationChannelRequest(
            name=name,
            notification_channel=notification_channel,
        )
        return self._inner_api_calls['create_notification_channel'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def update_notification_channel(
            self,
            notification_channel,
            update_mask=None,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Updates a notification channel. Fields not specified in the field mask
        remain unchanged.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> # TODO: Initialize ``notification_channel``:
            >>> notification_channel = {}
            >>>
            >>> response = client.update_notification_channel(notification_channel)

        Args:
            notification_channel (Union[dict, ~google.cloud.monitoring_v3.types.NotificationChannel]): A description of the changes to be applied to the specified
                notification channel. The description must provide a definition for
                fields to be updated; the names of these fields should also be
                included in the ``update_mask``.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.NotificationChannel`
            update_mask (Union[dict, ~google.cloud.monitoring_v3.types.FieldMask]): The fields to update.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.FieldMask`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.NotificationChannel` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'update_notification_channel' not in self._inner_api_calls:
            self._inner_api_calls[
                'update_notification_channel'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    UpdateNotificationChannel,
                    default_retry=self._method_configs[
                        'UpdateNotificationChannel'].retry,
                    default_timeout=self._method_configs[
                        'UpdateNotificationChannel'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.UpdateNotificationChannelRequest(
            notification_channel=notification_channel,
            update_mask=update_mask,
        )
        return self._inner_api_calls['update_notification_channel'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def delete_notification_channel(
            self,
            name,
            force=None,
            retry=google.api_core.gapic_v1.method.DEFAULT,
            timeout=google.api_core.gapic_v1.method.DEFAULT,
            metadata=None):
        """
        Deletes a notification channel.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.NotificationChannelServiceClient()
            >>>
            >>> name = client.notification_channel_path('[PROJECT]', '[NOTIFICATION_CHANNEL]')
            >>>
            >>> client.delete_notification_channel(name)

        Args:
            name (str): The channel for which to execute the request. The format is
                ``projects/[PROJECT_ID]/notificationChannels/[CHANNEL_ID]``.
            force (bool): If true, the notification channel will be deleted regardless of its
                use in alert policies (the policies will be updated to remove the
                channel). If false, channels that are still referenced by an existing
                alerting policy will fail to be deleted in a delete operation.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        if 'delete_notification_channel' not in self._inner_api_calls:
            self._inner_api_calls[
                'delete_notification_channel'] = google.api_core.gapic_v1.method.wrap_method(
                    self._notification_channel_service_stub.
                    DeleteNotificationChannel,
                    default_retry=self._method_configs[
                        'DeleteNotificationChannel'].retry,
                    default_timeout=self._method_configs[
                        'DeleteNotificationChannel'].timeout,
                    client_info=self._client_info,
                )

        request = notification_service_pb2.DeleteNotificationChannelRequest(
            name=name,
            force=force,
        )
        self._inner_api_calls['delete_notification_channel'](
            request, retry=retry, timeout=timeout, metadata=metadata)
