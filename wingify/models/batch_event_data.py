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


class BatchEventData:
    def __init__(self, events_per_request: int = 100, request_time_interval: int = 600, flush_callback=None):
        """
        Initialize the BatchEventData model with optional parameters.
        
        :param events_per_request: The number of events to send per batch (default is 100).
        :param request_time_interval: The time interval (in seconds) between batch requests (default is 600 seconds).
        """
        self.events_per_request = events_per_request  # Default value: 100
        self.request_time_interval = request_time_interval  # Default value: 600
        self.flush_callback = flush_callback

    def get_events_per_request(self) -> int:
        """
        Get the number of events to send per batch.
        """
        return self.events_per_request

    def set_events_per_request(self, events_per_request: int) -> None:
        """
        Set the number of events to send per batch.
        
        :param events_per_request: The number of events to send per batch.
        """
        self.events_per_request = events_per_request

    def get_request_time_interval(self) -> int:
        """
        Get the time interval (in seconds) between batch requests.
        """
        return self.request_time_interval

    def set_request_time_interval(self, request_time_interval: int) -> None:
        """
        Set the time interval (in seconds) between batch requests.
        
        :param request_time_interval: The time interval between batch requests in seconds.
        """
        self.request_time_interval = request_time_interval
    
    def get_flush_callback(self):
        """
        Get the flush callback function.
        """
        return self.flush_callback

    def set_flush_callback(self, flush_callback: None):
        """
        Set the flush callback function.
        
        :param flush_callback: The callback function to be set.
        """
        self.flush_callback = flush_callback