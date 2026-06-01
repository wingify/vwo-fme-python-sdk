# Copyright 2024-2026 Wingify Software Pvt. Ltd.
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

from typing import Dict, Optional

from wingify.models.batch_event_data import BatchEventData


class WingifyOptionsModel:
    """
    Canonical SDK options model. Accepts both Wingify and legacy VWO option keys
    for builder and metadata fields.
    """

    def __init__(self, options: Dict):
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

        # Builder: prefer wingifyBuilder, fall back to legacy vwoBuilder
        self.wingifyBuilder = options.get("wingifyBuilder") or options.get("vwoBuilder")
        self.vwoBuilder = self.wingifyBuilder

        self.is_usage_stats_disabled = options.get("is_usage_stats_disabled", False)

        # Meta: prefer _wingify_meta, fall back to legacy _vwo_meta
        self._wingify_meta = options.get("_wingify_meta") or options.get("_vwo_meta")
        self._vwo_meta = self._wingify_meta

        self.isAliasingEnabled = options.get("isAliasingEnabled", False)
        self.proxy_url = options.get("proxy_url", None)

        batch_event_data = options.get("batch_event_data", None)
        if batch_event_data:
            self.batchEventData = BatchEventData(
                events_per_request=batch_event_data.get("events_per_request"),
                request_time_interval=batch_event_data.get("request_time_interval"),
                flush_callback=batch_event_data.get("flush_callback", None),
            )
        else:
            self.batchEventData = None

    def get_account_id(self) -> str:
        return self.accountId

    def get_sdk_key(self) -> str:
        return self.sdkKey

    def get_is_development_mode(self) -> bool:
        return self.isDevelopmentMode

    def get_storage_service(self):
        return self.storage

    def get_gateway_service(self):
        return self.gateway_service

    def get_poll_interval(self) -> int:
        return self.poll_interval

    def get_logger(self):
        return self.logger

    def get_segmentation(self):
        return self.segmentation

    def get_integrations(self):
        return self.integrations

    def get_network(self):
        return self.network

    def get_wingify_builder(self):
        return self.wingifyBuilder

    def get_vwo_builder(self):
        """Legacy alias for get_wingify_builder()."""
        return self.wingifyBuilder

    def get_batch_event_data(self):
        return self.batchEventData

    def get_is_usage_stats_disabled(self) -> bool:
        return self.is_usage_stats_disabled

    def get_sdk_meta(self) -> Dict:
        return self._wingify_meta

    def get_vwo_meta(self) -> Dict:
        """Legacy alias for get_sdk_meta()."""
        return self._wingify_meta

    def get_wingify_meta(self) -> Dict:
        return self._wingify_meta

    def get_sdk_name(self) -> Optional[str]:
        meta = self._wingify_meta or {}
        return meta.get("_wingify_sdkName") or meta.get("_vwo_sdkName")

    def get_sdk_version(self) -> Optional[str]:
        meta = self._wingify_meta or {}
        return meta.get("_wingify_sdkVersion") or meta.get("_vwo_sdkVersion")

    def get_is_aliasing_enabled(self) -> bool:
        return self.isAliasingEnabled

    def set_is_aliasing_enabled(self, is_aliasing_enabled: bool) -> None:
        self.isAliasingEnabled = is_aliasing_enabled

    def get_proxy_url(self) -> str:
        return self.proxy_url
