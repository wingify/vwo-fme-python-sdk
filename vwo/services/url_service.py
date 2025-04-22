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


from typing import Optional


class UrlService:
    def __init__(self, collection_prefix=None):
        """
        Initializes the UrlService with an optional collection_prefix.
        If provided, this value is set after validation.

        :param collection_prefix: Optional prefix for URL collections.
        """
        if self._is_valid_string(collection_prefix):
            UrlService.collection_prefix = collection_prefix
        else:
            UrlService.collection_prefix = None

    @staticmethod
    def get_base_url():
        """
        Retrieves the base URL.
        If the gateway service is provided, it returns that;
        otherwise, it constructs the URL using base_url and collection_prefix.

        :return: The base URL.
        """
        from .settings_manager import SettingsManager

        settings_manager = SettingsManager.get_instance()
        base_url = settings_manager.hostname

        if settings_manager.is_gateway_service_provided:
            return base_url

        if hasattr(UrlService, "collection_prefix") and UrlService.collection_prefix:
            return f"{base_url}/{UrlService.collection_prefix}"

        return base_url

    @staticmethod
    def _is_valid_string(value):
        """
        Validates if the provided value is a valid string.

        :param value: The value to validate.
        :return: True if valid string, False otherwise.
        """
        return isinstance(value, str) and bool(value.strip())
