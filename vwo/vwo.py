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


from typing import Dict, Any, Optional
import time
from vwo.vwo_builder import VWOBuilder
from vwo.vwo_client import VWOClient
from vwo.enums.url_enum import UrlEnum
from vwo.utils.event_util import send_sdk_init_event, send_sdk_usage_stats_event
from vwo.utils.uuid_util import get_uuid as uuid_util_get_uuid
from vwo.utils.data_type_util import is_string


class VWO:
    vwo_builder: "VWOBuilder" = None
    instance: "VWOClient" = None

    def __init__(self, options: Dict):
        VWO.set_instance(options)

    @staticmethod
    def set_instance(options: Dict) -> "VWOClient":
        options_vwo_builder = options.get("vwoBuilder", None)
        VWO.vwo_builder = options_vwo_builder or VWOBuilder(options)

        # Configure the builder
        VWO.vwo_builder.set_logger().set_settings_manager().set_storage().set_network_manager().set_segmentation().init_polling().init_usage_stats()

        # Fetch settings synchronously and build the VWO instance
        settings = VWO.vwo_builder.get_settings(force=False)
        VWO.instance = VWO.vwo_builder.build(settings)
        VWO.instance.settings_fetch_time = VWO.vwo_builder.setting_file_manager.settings_fetch_time
        VWO.instance.is_settings_valid_on_init = VWO.vwo_builder.setting_file_manager.is_settings_valid_on_init
        
        # Initialize batching
        VWO.vwo_builder.init_batching()
        return VWO.instance

    @staticmethod
    def getInstance() -> Optional["VWO"]:
        return VWO.instance


def init(options: Dict[str, Any]) -> Optional["VWOClient"]:
    # Start timer for total init time
    start_time_for_init = time.time() * 1000  # Convert to milliseconds
    
    if not options or "sdk_key" not in options or not options["sdk_key"]:
        print(
            "SDK key is required to initialize VWO. Please provide the sdk_key in the options.",
            None,
        )
        return None

    if not options or "account_id" not in options or not options["account_id"]:
        print(
            "Account ID is required to initialize VWO. Please provide the account_id in the options.",
            None,
        )
        return None
    
    if options.get("is_aliasing_enabled", False) and (not options.get("gateway_service", None) or not options.get("gateway_service", None).get("url")):
        print(
            "Gateway service URL is required when aliasing is enabled. Please provide the gateway_service in the options.",
            None,
        )
        return None
    
    try:
        instance = VWO.set_instance(options)
        
        # Calculate SDK init time
        sdk_init_time = int((time.time() * 1000) - start_time_for_init)

        # Check if original_settings is not None before accessing .get()
        was_initialized = False
        if instance.original_settings is not None:
            was_initialized = instance.original_settings.get("sdkMetaInfo", {}).get("wasInitializedEarlier")

        if instance.is_settings_valid_on_init and not was_initialized:
            send_sdk_init_event(instance.settings_fetch_time, sdk_init_time)

        # send sdk usage stats event
        # get usage stats account id from settings
        usage_stats_account_id = None
        if instance.original_settings is not None:
            usage_stats_account_id = instance.original_settings.get("usageStatsAccountId")
        
        if usage_stats_account_id:
            send_sdk_usage_stats_event(usage_stats_account_id)

        return instance
    except Exception as e:
        print("VWO initialization failed. Error:", e)
        return None

def getUUID(user_id: str, account_id: str) -> Optional[str]:
    """
    Generate a deterministic UUID for a given user and account combination.

    :param user_id: The user's ID (must be a non-empty string).
    :param account_id: The account ID (must be a non-empty string).
    :return: UUID without dashes in uppercase, or None on invalid input or error.
    """
    api_name = "getUUID"
    
    try:
        # Validate user_id
        if not is_string(user_id) or user_id == '':
            print(f"userId passed to {api_name} API is not of valid type.")
            return None
        
        # Validate account_id
        if not is_string(account_id) or account_id == '':
            print(f"accountId passed to {api_name} API is not of valid type.")
            return None
        
        # Call the UUID utility function
        return uuid_util_get_uuid(user_id, account_id)
        
    except Exception as error:
        print(f"API - {api_name} failed to execute. Trace: {error}")
        return None
