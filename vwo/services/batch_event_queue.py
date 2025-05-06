# Copyright 2024 Wingify Software Pvt. Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import threading
import queue
from typing import Dict, Any
from vwo.packages.network_layer.manager.network_manager import NetworkManager
from ..utils.network_util import send_post_batch_request 
from ..utils.log_message_util import error_messages, info_messages
from vwo.packages.logger.core.log_manager import LogManager

class BatchEventQueue:
    MAX_EVENTS_PER_REQUEST = 5000

    def __init__(self, events_per_request: int, request_time_interval: int, account_id: int, sdk_key: str, flush_callback=None):
        """
        Initializes the batch event queue with the provided parameters.
        
        :param events_per_request: The number of events to send per batch.
        :param request_time_interval: The time interval (in seconds) between batch requests.
        :param account_id: The account ID for the batch events.
        :param sdk_key: The SDK key for the batch events.
        :param flush_callback: Optional callback function that gets called when the queue is flushed.
        """
        self.batch_queue = []
        self.events_per_request = events_per_request
        self.request_time_interval = request_time_interval
        self.account_id = account_id
        self.sdk_key = sdk_key
        self.is_batch_processing = False
        self.lock = threading.Lock()
        self.flush_callback = flush_callback

        self.create_new_batch_timer()

    def enqueue(self, event_data: Dict[str, Any]):
        with self.lock:
            self.batch_queue.append(event_data)
            # Print the current batch queue size
            LogManager.get_instance().info(
                info_messages.get('BATCH_QUEUE_SIZE').format(
                    size=len(self.batch_queue)
                )
            )

            # If batch size reaches the limit, trigger flush
            if len(self.batch_queue) >= self.events_per_request:
                self.flush()

    def create_new_batch_timer(self):
        """Create a timer to flush the batch queue at the specified interval."""
        self.timer = threading.Timer(self.request_time_interval, self.flush)
        self.timer.start()

    def clear_request_timer(self):
        """
        Cancels the timer if it exists.
        """
        if self.timer:
            self.timer.cancel()  # Cancel the ongoing timer

    def flush_and_clear_timer(self):
        """
        Flushes the queue and clears the timer.
        """
        flush_result = self.flush(manual=True)
        if isinstance(self.timer, threading.Timer):
            self.clear_request_timer()  # Cancel the request timer

        return flush_result

    def flush(self, manual=False):
        self.is_batch_processing = True
        if manual:
            LogManager.get_instance().info(
                info_messages.get('BATCH_FLUSH_MANUAL')
            )


        events_to_send = self.batch_queue[:]  
        self.batch_queue.clear()

        # Log before sending batch events
        LogManager.get_instance().info(
            info_messages.get('BATCH_FLUSH_STARTED').format(
                eventCount=len(events_to_send)
            )
        )
        network_instance = NetworkManager.get_instance()
        is_sent_successfully = False

        # Use background thread to handle the batch event sending
        def send_request():
            try:
                is_sent_successfully = self.send_batch_events(events_to_send)
                if is_sent_successfully:
                    LogManager.get_instance().info(
                        info_messages.get('BATCH_FLUSH_SUCCESS').format(
                            eventCount=len(events_to_send)
                        )
                    )
                else:
                    LogManager.get_instance().error(
                        error_messages.get("BATCH_FLUSH_FAILED")
                    )
                    self.batch_queue.extend(events_to_send)
            except Exception as e:
                LogManager.get_instance().error(
                    error_messages.get("BATCH_FLUSH_ERROR").format(
                        error=str(e)
                    )
                )
                self.batch_queue.extend(events_to_send)
            finally:
                # Reset the flag after flush
                self.is_batch_processing = False

        # Execute the batch sending in the background thread
        network_instance.execute_in_background(send_request)
        self.clear_request_timer()
        self.create_new_batch_timer()
        return is_sent_successfully

    def send_batch_events(self, events):
        """ Send the batch events asynchronously. """
        try:
            is_sent_successfully = send_post_batch_request(events, self.account_id, self.sdk_key, self.flush_callback)
            return is_sent_successfully
        except Exception as ex:
            LogManager.get_instance().error(
                error_messages.get("BATCH_FLUSH_ERROR").format(
                    error=str(ex)
                )
            )
            return False
