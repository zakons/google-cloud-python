# Copyright 2017, Google LLC
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

from __future__ import absolute_import

import collections
import copy
import logging
import random
import threading
import time

import six

from google.cloud.pubsub_v1.subscriber._protocol import requests


_LOGGER = logging.getLogger(__name__)
_LEASE_WORKER_NAME = 'Thread-LeaseMaintainer'


_LeasedMessage = collections.namedtuple(
    '_LeasedMessage',
    ['added_time', 'size'])


class Leaser(object):
    def __init__(self, subscriber):
        self._thread = None
        self._subscriber = subscriber

        self._leased_messages = {}
        """dict[str, float]: A mapping of ack IDs to the local time when the
            ack ID was initially leased in seconds since the epoch."""
        self._bytes = 0
        """int: The total number of bytes consumed by leased messages."""

        self._stop_event = threading.Event()

    @property
    def message_count(self):
        """int: The number of leased messages."""
        return len(self._leased_messages)

    @property
    def ack_ids(self):
        """Sequence[str]: The ack IDs of all leased messages."""
        return self._leased_messages.keys()

    @property
    def bytes(self):
        """int: The total size, in bytes, of all leased messages."""
        return self._bytes

    def add(self, items):
        """Add messages to be managed by the leaser."""
        for item in items:
            # Add the ack ID to the set of managed ack IDs, and increment
            # the size counter.
            if item.ack_id not in self._leased_messages:
                self._leased_messages[item.ack_id] = _LeasedMessage(
                    added_time=time.time(),
                    size=item.byte_size)
                self._bytes += item.byte_size
            else:
                _LOGGER.debug(
                    'Message %s is already lease managed', item.ack_id)

    def remove(self, items):
        """Remove messages from lease management."""
        # Remove the ack ID from lease management, and decrement the
        # byte counter.
        for item in items:
            if self._leased_messages.pop(item.ack_id, None) is not None:
                self._bytes -= item.byte_size
            else:
                _LOGGER.debug('Item %s was not managed.', item.ack_id)

        if self._bytes < 0:
            _LOGGER.debug(
                'Bytes was unexpectedly negative: %d', self._bytes)
            self._bytes = 0

    def maintain_leases(self):
        """Maintain all of the leases being managed by the subscriber.

        This method modifies the ack deadline for all of the managed
        ack IDs, then waits for most of that time (but with jitter), and
        repeats.
        """
        while self._subscriber.is_active and not self._stop_event.is_set():
            # Determine the appropriate duration for the lease. This is
            # based off of how long previous messages have taken to ack, with
            # a sensible default and within the ranges allowed by Pub/Sub.
            p99 = self._subscriber.ack_histogram.percentile(99)
            _LOGGER.debug('The current p99 value is %d seconds.', p99)

            # Make a copy of the leased messages. This is needed because it's
            # possible for another thread to modify the dictionary while
            # we're iterating over it.
            leased_messages = copy.copy(self._leased_messages)

            # Drop any leases that are well beyond max lease time. This
            # ensures that in the event of a badly behaving actor, we can
            # drop messages and allow Pub/Sub to resend them.
            cutoff = (
                time.time() -
                self._subscriber.flow_control.max_lease_duration)
            to_drop = [
                requests.DropRequest(ack_id, item.size)
                for ack_id, item
                in six.iteritems(leased_messages)
                if item.added_time < cutoff]

            if to_drop:
                _LOGGER.warning(
                    'Dropping %s items because they were leased too long.',
                    len(to_drop))
                self._subscriber.drop(to_drop)

            # Remove dropped items from our copy of the leased messages (they
            # have already been removed from the real one by
            # self._subscriber.drop(), which calls self.remove()).
            for item in to_drop:
                leased_messages.pop(item.ack_id)

            # Create a streaming pull request.
            # We do not actually call `modify_ack_deadline` over and over
            # because it is more efficient to make a single request.
            ack_ids = leased_messages.keys()
            if ack_ids:
                _LOGGER.debug('Renewing lease for %d ack IDs.', len(ack_ids))

                # NOTE: This may not work as expected if ``consumer.active``
                #       has changed since we checked it. An implementation
                #       without any sort of race condition would require a
                #       way for ``send_request`` to fail when the consumer
                #       is inactive.
                self._subscriber.modify_ack_deadline([
                    requests.ModAckRequest(ack_id, p99) for ack_id in ack_ids])

            # Now wait an appropriate period of time and do this again.
            #
            # We determine the appropriate period of time based on a random
            # period between 0 seconds and 90% of the lease. This use of
            # jitter (http://bit.ly/2s2ekL7) helps decrease contention in cases
            # where there are many clients.
            snooze = random.uniform(0.0, p99 * 0.9)
            _LOGGER.debug('Snoozing lease management for %f seconds.', snooze)
            time.sleep(snooze)

        _LOGGER.info('%s exiting.', _LEASE_WORKER_NAME)

    def start(self):
        if self._thread is not None:
            raise ValueError('Leaser is already running.')

        # Create and start the helper thread.
        self._stop_event.clear()
        thread = threading.Thread(
            name=_LEASE_WORKER_NAME,
            target=self.maintain_leases)
        thread.daemon = True
        thread.start()
        _LOGGER.debug('Started helper thread %s', thread.name)
        self._thread = thread

    def stop(self):
        self._stop_event.set()

        if self._thread is not None:
            # The thread should automatically exit when the consumer is
            # inactive.
            self._thread.join()

        self._thread = None
