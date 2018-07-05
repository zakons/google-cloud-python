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
"""Accesses the google.monitoring.v3 AlertPolicyService API."""

import functools
import pkg_resources

import google.api_core.gapic_v1.client_info
import google.api_core.gapic_v1.config
import google.api_core.gapic_v1.method
import google.api_core.grpc_helpers
import google.api_core.page_iterator
import google.api_core.path_template
import grpc

from google.cloud.monitoring_v3.gapic import alert_policy_service_client_config
from google.cloud.monitoring_v3.gapic import enums
from google.cloud.monitoring_v3.proto import alert_pb2
from google.cloud.monitoring_v3.proto import alert_service_pb2
from google.cloud.monitoring_v3.proto import alert_service_pb2_grpc
from google.protobuf import empty_pb2
from google.protobuf import field_mask_pb2

_GAPIC_LIBRARY_VERSION = pkg_resources.get_distribution(
    'google-cloud-monitoring', ).version


class AlertPolicyServiceClient(object):
    """
    The AlertPolicyService API is used to manage (list, create, delete,
    edit) alert policies in Stackdriver Monitoring. An alerting policy is
    a description of the conditions under which some aspect of your
    system is considered to be \"unhealthy\" and the ways to notify
    people or services about this state. In addition to using this API, alert
    policies can also be managed through
    `Stackdriver Monitoring <https://cloud.google.com/monitoring/docs/>`_,
    which can be reached by clicking the \"Monitoring\" tab in
    `Cloud Console <https://console.cloud.google.com/>`_.
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
    _INTERFACE_NAME = 'google.monitoring.v3.AlertPolicyService'

    @classmethod
    def project_path(cls, project):
        """Return a fully-qualified project string."""
        return google.api_core.path_template.expand(
            'projects/{project}',
            project=project,
        )

    @classmethod
    def alert_policy_path(cls, project, alert_policy):
        """Return a fully-qualified alert_policy string."""
        return google.api_core.path_template.expand(
            'projects/{project}/alertPolicies/{alert_policy}',
            project=project,
            alert_policy=alert_policy,
        )

    @classmethod
    def alert_policy_condition_path(cls, project, alert_policy, condition):
        """Return a fully-qualified alert_policy_condition string."""
        return google.api_core.path_template.expand(
            'projects/{project}/alertPolicies/{alert_policy}/conditions/{condition}',
            project=project,
            alert_policy=alert_policy,
            condition=condition,
        )

    def __init__(self,
                 channel=None,
                 credentials=None,
                 client_config=alert_policy_service_client_config.config,
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
        self._alert_policy_service_stub = (
            alert_service_pb2_grpc.AlertPolicyServiceStub(self.channel))

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
        self._alert_policy_service_stub = (
            alert_service_pb2_grpc.AlertPolicyServiceStub(self.channel))
        self._inner_api_calls.clear()

    # Service calls
    def list_alert_policies(self,
                            name,
                            filter_=None,
                            order_by=None,
                            page_size=None,
                            retry=google.api_core.gapic_v1.method.DEFAULT,
                            timeout=google.api_core.gapic_v1.method.DEFAULT,
                            metadata=None):
        """
        Lists the existing alerting policies for the project.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.AlertPolicyServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_alert_policies(name):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_alert_policies(name, options=CallOptions(page_token=INITIAL_PAGE)):
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            name (str): The project whose alert policies are to be listed. The format is

                    projects/[PROJECT_ID]

                Note that this field names the parent container in which the alerting
                policies to be listed are stored. To retrieve a single alerting policy
                by name, use the
                ``GetAlertPolicy``
                operation, instead.
            filter_ (str): If provided, this field specifies the criteria that must be met by
                alert policies to be included in the response.

                For more details, see [sorting and
                filtering](/monitoring/api/v3/sorting-and-filtering).
            order_by (str): A comma-separated list of fields by which to sort the result. Supports
                the same set of field references as the ``filter`` field. Entries can be
                prefixed with a minus sign to sort by the field in descending order.

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
            is an iterable of :class:`~google.cloud.monitoring_v3.types.AlertPolicy` instances.
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
        if 'list_alert_policies' not in self._inner_api_calls:
            self._inner_api_calls[
                'list_alert_policies'] = google.api_core.gapic_v1.method.wrap_method(
                    self._alert_policy_service_stub.ListAlertPolicies,
                    default_retry=self._method_configs[
                        'ListAlertPolicies'].retry,
                    default_timeout=self._method_configs['ListAlertPolicies']
                    .timeout,
                    client_info=self._client_info,
                )

        request = alert_service_pb2.ListAlertPoliciesRequest(
            name=name,
            filter=filter_,
            order_by=order_by,
            page_size=page_size,
        )
        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls['list_alert_policies'],
                retry=retry,
                timeout=timeout,
                metadata=metadata),
            request=request,
            items_field='alert_policies',
            request_token_field='page_token',
            response_token_field='next_page_token',
        )
        return iterator

    def get_alert_policy(self,
                         name,
                         retry=google.api_core.gapic_v1.method.DEFAULT,
                         timeout=google.api_core.gapic_v1.method.DEFAULT,
                         metadata=None):
        """
        Gets a single alerting policy.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.AlertPolicyServiceClient()
            >>>
            >>> name = client.alert_policy_path('[PROJECT]', '[ALERT_POLICY]')
            >>>
            >>> response = client.get_alert_policy(name)

        Args:
            name (str): The alerting policy to retrieve. The format is

                    projects/[PROJECT_ID]/alertPolicies/[ALERT_POLICY_ID]
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.AlertPolicy` instance.

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
        if 'get_alert_policy' not in self._inner_api_calls:
            self._inner_api_calls[
                'get_alert_policy'] = google.api_core.gapic_v1.method.wrap_method(
                    self._alert_policy_service_stub.GetAlertPolicy,
                    default_retry=self._method_configs['GetAlertPolicy'].retry,
                    default_timeout=self._method_configs['GetAlertPolicy']
                    .timeout,
                    client_info=self._client_info,
                )

        request = alert_service_pb2.GetAlertPolicyRequest(name=name, )
        return self._inner_api_calls['get_alert_policy'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def create_alert_policy(self,
                            name,
                            alert_policy,
                            retry=google.api_core.gapic_v1.method.DEFAULT,
                            timeout=google.api_core.gapic_v1.method.DEFAULT,
                            metadata=None):
        """
        Creates a new alerting policy.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.AlertPolicyServiceClient()
            >>>
            >>> name = client.project_path('[PROJECT]')
            >>>
            >>> # TODO: Initialize ``alert_policy``:
            >>> alert_policy = {}
            >>>
            >>> response = client.create_alert_policy(name, alert_policy)

        Args:
            name (str): The project in which to create the alerting policy. The format is
                ``projects/[PROJECT_ID]``.

                Note that this field names the parent container in which the alerting
                policy will be written, not the name of the created policy. The alerting
                policy that is returned will have a name that contains a normalized
                representation of this name as a prefix but adds a suffix of the form
                ``/alertPolicies/[POLICY_ID]``, identifying the policy in the container.
            alert_policy (Union[dict, ~google.cloud.monitoring_v3.types.AlertPolicy]): The requested alerting policy. You should omit the ``name`` field in this
                policy. The name will be returned in the new policy, including
                a new [ALERT_POLICY_ID] value.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.AlertPolicy`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will not
                be retried.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.monitoring_v3.types.AlertPolicy` instance.

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
        if 'create_alert_policy' not in self._inner_api_calls:
            self._inner_api_calls[
                'create_alert_policy'] = google.api_core.gapic_v1.method.wrap_method(
                    self._alert_policy_service_stub.CreateAlertPolicy,
                    default_retry=self._method_configs[
                        'CreateAlertPolicy'].retry,
                    default_timeout=self._method_configs['CreateAlertPolicy']
                    .timeout,
                    client_info=self._client_info,
                )

        request = alert_service_pb2.CreateAlertPolicyRequest(
            name=name,
            alert_policy=alert_policy,
        )
        return self._inner_api_calls['create_alert_policy'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def delete_alert_policy(self,
                            name,
                            retry=google.api_core.gapic_v1.method.DEFAULT,
                            timeout=google.api_core.gapic_v1.method.DEFAULT,
                            metadata=None):
        """
        Deletes an alerting policy.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.AlertPolicyServiceClient()
            >>>
            >>> name = client.alert_policy_path('[PROJECT]', '[ALERT_POLICY]')
            >>>
            >>> client.delete_alert_policy(name)

        Args:
            name (str): The alerting policy to delete. The format is:

                    projects/[PROJECT_ID]/alertPolicies/[ALERT_POLICY_ID]

                For more information, see ``AlertPolicy``.
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
        if 'delete_alert_policy' not in self._inner_api_calls:
            self._inner_api_calls[
                'delete_alert_policy'] = google.api_core.gapic_v1.method.wrap_method(
                    self._alert_policy_service_stub.DeleteAlertPolicy,
                    default_retry=self._method_configs[
                        'DeleteAlertPolicy'].retry,
                    default_timeout=self._method_configs['DeleteAlertPolicy']
                    .timeout,
                    client_info=self._client_info,
                )

        request = alert_service_pb2.DeleteAlertPolicyRequest(name=name, )
        self._inner_api_calls['delete_alert_policy'](
            request, retry=retry, timeout=timeout, metadata=metadata)

    def update_alert_policy(self,
                            alert_policy,
                            update_mask=None,
                            retry=google.api_core.gapic_v1.method.DEFAULT,
                            timeout=google.api_core.gapic_v1.method.DEFAULT,
                            metadata=None):
        """
        Updates an alerting policy. You can either replace the entire policy with
        a new one or replace only certain fields in the current alerting policy by
        specifying the fields to be updated via ``updateMask``. Returns the
        updated alerting policy.

        Example:
            >>> from google.cloud import monitoring_v3
            >>>
            >>> client = monitoring_v3.AlertPolicyServiceClient()
            >>>
            >>> # TODO: Initialize ``alert_policy``:
            >>> alert_policy = {}
            >>>
            >>> response = client.update_alert_policy(alert_policy)

        Args:
            alert_policy (Union[dict, ~google.cloud.monitoring_v3.types.AlertPolicy]): Required. The updated alerting policy or the updated values for the
                fields listed in ``update_mask``.
                If ``update_mask`` is not empty, any fields in this policy that are
                not in ``update_mask`` are ignored.
                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.monitoring_v3.types.AlertPolicy`
            update_mask (Union[dict, ~google.cloud.monitoring_v3.types.FieldMask]): Optional. A list of alerting policy field names. If this field is not
                empty, each listed field in the existing alerting policy is set to the
                value of the corresponding field in the supplied policy (``alert_policy``),
                or to the field's default value if the field is not in the supplied
                alerting policy.  Fields not listed retain their previous value.

                Examples of valid field masks include ``display_name``, ``documentation``,
                ``documentation.content``, ``documentation.mime_type``, ``user_labels``,
                ``user_label.nameofkey``, ``enabled``, ``conditions``, ``combiner``, etc.

                If this field is empty, then the supplied alerting policy replaces the
                existing policy. It is the same as deleting the existing policy and
                adding the supplied policy, except for the following:

                +   The new policy will have the same ``[ALERT_POLICY_ID]`` as the former
                    policy. This gives you continuity with the former policy in your
                    notifications and incidents.
                +   Conditions in the new policy will keep their former ``[CONDITION_ID]`` if
                    the supplied condition includes the `name` field with that
                    `[CONDITION_ID]`. If the supplied condition omits the `name` field,
                    then a new `[CONDITION_ID]` is created.

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
            A :class:`~google.cloud.monitoring_v3.types.AlertPolicy` instance.

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
        if 'update_alert_policy' not in self._inner_api_calls:
            self._inner_api_calls[
                'update_alert_policy'] = google.api_core.gapic_v1.method.wrap_method(
                    self._alert_policy_service_stub.UpdateAlertPolicy,
                    default_retry=self._method_configs[
                        'UpdateAlertPolicy'].retry,
                    default_timeout=self._method_configs['UpdateAlertPolicy']
                    .timeout,
                    client_info=self._client_info,
                )

        request = alert_service_pb2.UpdateAlertPolicyRequest(
            alert_policy=alert_policy,
            update_mask=update_mask,
        )
        return self._inner_api_calls['update_alert_policy'](
            request, retry=retry, timeout=timeout, metadata=metadata)
