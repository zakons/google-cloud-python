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
"""Accesses the google.monitoring.v3 GroupService API."""

import functools
import pkg_resources

import google.api_core.gapic_v1.client_info
import google.api_core.gapic_v1.config
import google.api_core.gapic_v1.method
import google.api_core.grpc_helpers
import google.api_core.page_iterator
import google.api_core.path_template
import google.api_core.protobuf_helpers
import grpc

from google.cloud.monitoring_v3.gapic import enums
from google.cloud.monitoring_v3.gapic import group_service_client_config
from google.cloud.monitoring_v3.proto import alert_pb2
from google.cloud.monitoring_v3.proto import alert_service_pb2
from google.cloud.monitoring_v3.proto import alert_service_pb2_grpc
from google.cloud.monitoring_v3.proto import common_pb2
from google.cloud.monitoring_v3.proto import group_pb2
from google.cloud.monitoring_v3.proto import group_service_pb2
from google.cloud.monitoring_v3.proto import group_service_pb2_grpc
from google.protobuf import empty_pb2
from google.protobuf import field_mask_pb2

_GAPIC_LIBRARY_VERSION = pkg_resources.get_distribution(
    'google-cloud-monitoring', ).version


class GroupServiceClient(object):
    """
    The Group API lets you inspect and manage your
    `groups <https://cloud.google.comgoogle.monitoring.v3.Group>`_.

    A group is a named filter that is used to identify
    a collection of monitored resources. Groups are typically used to
    mirror the physical and/or logical topology of the environment.
    Because group membership is computed dynamically, monitored
    resources that are started in the future are automatically placed
    in matching groups. By using a group to name monitored resources in,
    for example, an alert policy, the target of that alert policy is
    updated automatically as monitored resources are added and removed
    from the infrastructure.
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
    _INTERFACE_NAME = 'google.monitoring.v3.GroupService'

    @classmethod
    def project_path(cls, project):
        """Return a fully-qualified project string."""
        return google.api_core.path_template.expand(
            'projects/{project}',
            project=project,
        )

    @classmethod
    def group_path(cls, project, group):
        """Return a fully-qualified group string."""
        return google.api_core.path_template.expand(
            'projects/{project}/groups/{group}',
            project=project,
            group=group,
        )

    def __init__(self,
                 channel=None,
                 credentials=None,
                 client_config=group_service_client_config.config,
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
        self._group_service_stub = (group_service_pb2_grpc.GroupServiceStub(
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
        self._group_service_stub = (group_service_pb2_grpc.GroupServiceStub(
            self.channel))
        self._inner_api_calls.clear()

    # Service calls
    def list_groups(self,
                    name,
                    children_of_group=None,
                    ancestors_of_group=None,
                    descendants_of_group=None,
                    page_size=None,
                    retry=google.api_core.gapic_v1.method.DEFAULT,
                    timeout=google.api_core.gapic_v1.method.DEFAULT,
                    metadata=None):
        """
        Lists the existing groups.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.GroupServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_groups(name):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_groups(name, options=CallOptions(page_token=INITIAL_PAGE)):
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            name (str): The project whose groups are to be listed. The format is
                ``\"projects/{project_id_or_number}\"``.
            children_of_group (str): A group name: ``\"projects/{project_id_or_number}/groups/{group_id}\"``.
                Returns groups whose ``parentName`` field contains the group
                name.  If no groups have this parent, the results are empty.
            ancestors_of_group (str): A group name: ``\"projects/{project_id_or_number}/groups/{group_id}\"``.
                Returns groups that are ancestors of the specified group.
                The groups are returned in order, starting with the immediate parent and
                ending with the most distant ancestor.  If the specified group has no
                immediate parent, the results are empty.
            descendants_of_group (str): A group name: ``\"projects/{project_id_or_number}/groups/{group_id}\"``.
                Returns the descendants of the specified group.  This is a superset of
                the results returned by the ``childrenOfGroup`` filter, and includes
                children-of-children, and so forth.
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
            is an iterable of :class:`~google.cloud.monitoring_v3.types.Group` instances.
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
        if 'list_groups' not in self._inner_api_calls:
            self._inner_api_calls[
                'list_groups'] = google.api_core.gapic_v1.method.wrap_method(
                    self._group_service_stub.ListGroups,
                    default_retry=self._method_configs['ListGroups'].retry,
                    default_timeout=self._method_configs['ListGroups'].timeout,
                    client_info=self._client_info,
                )

        # Sanity check: We have some fields which are mutually exclusive;
        # raise ValueError if more than one is sent.
        google.api_core.protobuf_helpers.check_oneof(
            children_of_group=children_of_group,
            ancestors_of_group=ancestors_of_group,
            descendants_of_group=descendants_of_group,
        )

        request = group_service_pb2.ListGroupsRequest(
            name=name,
            children_of_group=children_of_group,
            ancestors_of_group=ancestors_of_group,
            descendants_of_group=descendants_of_group,
            page_size=page_size,
        )
        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls['list_groups'],
                retry=retry,
                timeout=timeout,
                metadata=metadata),
            request=request,
            items_field='group',
            request_token_field='page_token',
            response_token_field='next_page_token',
        )
        return iterator

    def get_group(self,
                  name,
                  retry=google.api_core.gapic_v1.method.DEFAULT,
                  timeout=google.api_core.gapic_v1.method.DEFAULT,
                  metadata=None):
        """
        Gets a single group.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.GroupServiceClient()
            >>>
            >>> name = client.group_path('[PROJECT]', '[GROUP]')
            >>>
            >>> response = client.get_group(name)

        Args:
            name (str): The group to retrieve. The format is
                ``\"projects/{project_id_or_number}/groups/{group_id}\"``.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.Group` instance.

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
        if 'get_group' not in self._inner_api_calls:
            self._inner_api_calls[
                'get_group'] = google.api_core.gapic_v1.method.wrap_method(
                    self._group_service_stub.GetGroup,
                    default_retry=self._method_configs['GetGroup'].retry,
                    default_timeout=self._method_configs['GetGroup'].timeout,
                    client_info=self._client_info,
                )

        request = group_service_pb2.GetGroupRequest(name=name, )
        return self._inner_api_calls['get_group'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def create_group(self,
                     name,
                     group,
                     validate_only=None,
                     retry=google.api_core.gapic_v1.method.DEFAULT,
                     timeout=google.api_core.gapic_v1.method.DEFAULT,
                     metadata=None):
        """
        Creates a new group.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.GroupServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # TODO: Initialize ``group``:
            >>> group = {}
            >>>
            >>> response = client.create_group(name, group)

        Args:
            name (str): The project in which to create the group. The format is
                ``\"projects/{project_id_or_number}\"``.
            group (Union[dict, ~google.cloud.monitoring_v3.types.Group]): A group definition. It is an error to define the ``name`` field because
                the system assigns the name.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.Group`
            validate_only (bool): If true, validate this request but do not create the group.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.Group` instance.

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
        if 'create_group' not in self._inner_api_calls:
            self._inner_api_calls[
                'create_group'] = google.api_core.gapic_v1.method.wrap_method(
                    self._group_service_stub.CreateGroup,
                    default_retry=self._method_configs['CreateGroup'].retry,
                    default_timeout=self._method_configs['CreateGroup']
                    .timeout,
                    client_info=self._client_info,
                )

        request = group_service_pb2.CreateGroupRequest(
            name=name,
            group=group,
            validate_only=validate_only,
        )
        return self._inner_api_calls['create_group'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def update_group(self,
                     group,
                     validate_only=None,
                     retry=google.api_core.gapic_v1.method.DEFAULT,
                     timeout=google.api_core.gapic_v1.method.DEFAULT,
                     metadata=None):
        """
        Updates an existing group.
        You can change any group attributes except ``name``.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.GroupServiceClient()
            >>>
            >>> # TODO: Initialize ``group``:
            >>> group = {}
            >>>
            >>> response = client.update_group(group)

        Args:
            group (Union[dict, ~google.cloud.monitoring_v3.types.Group]): The new definition of the group.  All fields of the existing group,
                excepting ``name``, are replaced with the corresponding fields of this group.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.Group`
            validate_only (bool): If true, validate this request but do not update the existing group.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.Group` instance.

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
        if 'update_group' not in self._inner_api_calls:
            self._inner_api_calls[
                'update_group'] = google.api_core.gapic_v1.method.wrap_method(
                    self._group_service_stub.UpdateGroup,
                    default_retry=self._method_configs['UpdateGroup'].retry,
                    default_timeout=self._method_configs['UpdateGroup']
                    .timeout,
                    client_info=self._client_info,
                )

        request = group_service_pb2.UpdateGroupRequest(
            group=group,
            validate_only=validate_only,
        )
        return self._inner_api_calls['update_group'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def delete_group(self,
                     name,
                     retry=google.api_core.gapic_v1.method.DEFAULT,
                     timeout=google.api_core.gapic_v1.method.DEFAULT,
                     metadata=None):
        """
        Deletes an existing group.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.GroupServiceClient()
            >>>
            >>> name = client.group_path('[PROJECT]', '[GROUP]')
            >>>
            >>> client.delete_group(name)

        Args:
            name (str): The group to delete. The format is
                ``\"projects/{project_id_or_number}/groups/{group_id}\"``.
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
        if 'delete_group' not in self._inner_api_calls:
            self._inner_api_calls[
                'delete_group'] = google.api_core.gapic_v1.method.wrap_method(
                    self._group_service_stub.DeleteGroup,
                    default_retry=self._method_configs['DeleteGroup'].retry,
                    default_timeout=self._method_configs['DeleteGroup']
                    .timeout,
                    client_info=self._client_info,
                )

        request = group_service_pb2.DeleteGroupRequest(name=name, )
        self._inner_api_calls['delete_group'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def list_group_members(self,
                           name,
                           page_size=None,
                           filter_=None,
                           interval=None,
                           retry=google.api_core.gapic_v1.method.DEFAULT,
                           timeout=google.api_core.gapic_v1.method.DEFAULT,
                           metadata=None):
        """
        Lists the monitored resources that are members of a group.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.GroupServiceClient()
            >>>
            >>> name = client.group_path('[PROJECT]', '[GROUP]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_group_members(name):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_group_members(name, options=CallOptions(page_token=INITIAL_PAGE)):
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            name (str): The group whose members are listed. The format is
                ``\"projects/{project_id_or_number}/groups/{group_id}\"``.
            page_size (int): The maximum number of resources contained in the
                underlying API response. If page streaming is performed per-
                resource, this parameter does not affect the return value. If page
                streaming is performed per-page, this determines the maximum number
                of resources in a page.
            filter_ (str): An optional `list filter <https://cloud.google.com/monitoring/api/learn_more#filtering>`_ describing
                the members to be returned.  The filter may reference the type, labels, and
                metadata of monitored resources that comprise the group.
                For example, to return only resources representing Compute Engine VM
                instances, use this filter:

                ::

                    resource.type = \"gce_instance\"
            interval (Union[dict, ~google.cloud.monitoring_v3.types.TimeInterval]): An optional time interval for which results should be returned. Only
                members that were part of the group during the specified interval are
                included in the response.  If no interval is provided then the group
                membership over the last minute is returned.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.TimeInterval`
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
            is an iterable of :class:`~google.cloud.monitoring_v3.types.MonitoredResource` instances.
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
        if 'list_group_members' not in self._inner_api_calls:
            self._inner_api_calls[
                'list_group_members'] = google.api_core.gapic_v1.method.wrap_method(
                    self._group_service_stub.ListGroupMembers,
                    default_retry=self._method_configs[
                        'ListGroupMembers'].retry,
                    default_timeout=self._method_configs['ListGroupMembers']
                    .timeout,
                    client_info=self._client_info,
                )

        request = group_service_pb2.ListGroupMembersRequest(
            name=name,
            page_size=page_size,
            filter=filter_,
            interval=interval,
        )
        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls['list_group_members'],
                retry=retry,
                timeout=timeout,
                metadata=metadata),
            request=request,
            items_field='members',
            request_token_field='page_token',
            response_token_field='next_page_token',
        )
        return iterator
