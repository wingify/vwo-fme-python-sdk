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

"""Brand-specific runtime values"""

from wingify.constants.Constants import Constants


def get_brand(is_via_vwo: bool) -> str:
    return Constants.VWO_BRAND_DISPLAY_NAME if is_via_vwo else Constants.WINGIFY_BRAND_DISPLAY_NAME


def get_log_prefix(is_via_vwo: bool) -> str:
    return Constants.VWO_LOG_PREFIX if is_via_vwo else Constants.WINGIFY_LOG_PREFIX


def get_sdk_name(is_via_vwo: bool) -> str:
    return Constants.VWO_SDK_NAME if is_via_vwo else Constants.WINGIFY_SDK_NAME


def get_settings_hostname(is_via_vwo: bool) -> str:
    return Constants.VWO_HOST_NAME if is_via_vwo else Constants.WINGIFY_SETTINGS_HOST_NAME


def get_events_hostname(is_via_vwo: bool) -> str:
    return Constants.VWO_HOST_NAME if is_via_vwo else Constants.WINGIFY_COLLECTION_HOST_NAME
