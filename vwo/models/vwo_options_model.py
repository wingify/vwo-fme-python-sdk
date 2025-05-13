# Copyright 2024-2025 Wingify Software Pvt. Ltd.
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


from typing import Dict

from vwo.models.batch_event_data import BatchEventData
class VWOOptionsModel:
    def __init__(self, options: Dict):
        """
        Initialize the VWOOptionsModel with the provided options.

        :param options: A dictionary containing the configuration options for VWO.
        """
        self.accountId = options.get("accountId", None)
        self.sdkKey = options.get("sdkKey", None)
        self.isDevelopmentMode = options.get("isDevelopmentMode", False)
        self.storage = options.get("storage", None)
        self.gateway_service = options.get("gateway_service", None)
        self.poll_interval = options.get("poll_interval", None)
        self.logger = options.get("logger", None)
        self.segmentation = options.get("segmentation", None)
        self.integrations = options.get("integrations", None)
        self.network = options.get("network", None)
        self.vwoBuilder = options.get("vwoBuilder", None)
        self.is_usage_stats_disabled = options.get("is_usage_stats_disabled", False)
        self._vwo_meta = options.get("_vwo_meta", None)

        # Initialize BatchEventData
        batch_event_data = options.get('batch_event_data', None)
        if batch_event_data:
            self.batchEventData = BatchEventData(
                events_per_request=batch_event_data.get('events_per_request'),
                request_time_interval=batch_event_data.get('request_time_interval'),
                flush_callback=batch_event_data.get('flush_callback', None)
            )
        else:
            self.batchEventData = None

    def get_account_id(self) -> str:
        """
        Get the account ID.

        :return: The account ID as a string.
        """
        return self.accountId

    def get_sdk_key(self) -> str:
        """
        Get the SDK key.

        :return: The SDK key as a string.
        """
        return self.sdkKey

    def get_is_development_mode(self) -> bool:
        """
        Check if development mode is enabled.

        :return: True if development mode is enabled, False otherwise.
        """
        return self.isDevelopmentMode

    def get_storage_service(self):
        """
        Get the storage service.

        :return: The storage service, which can be a Connector or a dictionary.
        """
        return self.storage

    def get_gateway_service(self):
        """
        Get the gateway service.

        :return: The gateway service instance.
        """
        return self.gateway_service

    def get_poll_interval(self) -> int:
        """
        Get the poll interval.

        :return: The poll interval as an integer.
        """
        return self.poll_interval

    def get_logger(self):
        """
        Get the logger instance.

        :return: The logger instance.
        """
        return self.logger

    def get_segmentation(self):
        """
        Get the segmentation evaluator.

        :return: The segmentation evaluator instance.
        """
        return self.segmentation

    def get_integrations(self):
        """
        Get the integration options.

        :return: The integration options instance.
        """
        return self.integrations

    def get_network(self):
        """
        Get the network options.

        :return: The network options instance.
        """
        return self.network

    def get_vwo_builder(self):
        """
        Get the VWO builder.

        :return: The VWO builder instance.
        """
        return self.vwoBuilder
    
    def get_batch_event_data(self):
        """
        Get the batch event data.
        
        :return: The BatchEventData instance.
        """
        return self.batchEventData
    
    def get_is_usage_stats_disabled(self) -> bool:
        """
        Check if usage stats are disabled.

        :return: True if usage stats are disabled, False otherwise.
        """
        return self.is_usage_stats_disabled

    def get_vwo_meta(self) -> Dict:
        """
        Get the VWO meta data.

        :return: The VWO meta data as a dictionary.
        """
        return self._vwo_meta