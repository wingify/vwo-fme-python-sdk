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


from typing import Dict, Any, Optional
import time

from wingify.wingify_builder import WingifyBuilder
from wingify.wingify_client import WingifyClient
from wingify.utils.event_util import send_sdk_init_event, send_sdk_usage_stats_event
from wingify.utils.uuid_util import get_uuid as uuid_util_get_uuid
from wingify.utils.data_type_util import is_string
from wingify.utils.brand_context import set_is_via_vwo
from wingify.utils.brand_util import get_brand
from wingify.utils.log_message_util import refresh_log_messages
from wingify.packages.logger.core.log_manager import LogManager
from wingify.services.internal_events_sampling_service import InternalEventsSamplingService


class Wingify:
    """
    Canonical SDK entry orchestrator. Initializes services, fetches settings,
    and returns a WingifyClient singleton.
    """

    wingify_builder: "WingifyBuilder" = None
    instance: "WingifyClient" = None

    def __init__(self, options: Dict):
        Wingify.set_instance(options)

    @staticmethod
    def set_instance(options: Dict) -> "WingifyClient":
        is_via_vwo = bool(options.get("is_via_vwo", False))
        set_is_via_vwo(is_via_vwo)
        refresh_log_messages(is_via_vwo)
        LogManager._instance = None

        # Accept both Wingify and legacy VWO builder option keys
        custom_builder = options.get("wingifyBuilder") or options.get("vwoBuilder")
        Wingify.wingify_builder = custom_builder or WingifyBuilder(options)

        Wingify.wingify_builder.set_logger().set_settings_manager().set_storage().set_network_manager().set_segmentation().init_polling().init_usage_stats()

        settings = Wingify.wingify_builder.get_settings(force=False)
        Wingify.instance = Wingify.wingify_builder.build(settings)
        Wingify.instance.settings_fetch_time = Wingify.wingify_builder.setting_file_manager.settings_fetch_time
        Wingify.instance.is_settings_valid_on_init = Wingify.wingify_builder.setting_file_manager.is_settings_valid_on_init

        Wingify.wingify_builder.init_batching()
        return Wingify.instance

    @staticmethod
    def getInstance() -> Optional["Wingify"]:
        return Wingify.instance


def init(options: Dict[str, Any]) -> Optional["WingifyClient"]:
    """Initialize the SDK and return a WingifyClient instance."""
    options = dict(options or {})
    if "is_via_vwo" not in options:
        options["is_via_vwo"] = False

    start_time_for_init = time.time() * 1000
    brand = get_brand(options["is_via_vwo"])

    if not options or "sdk_key" not in options or not options["sdk_key"]:
        print(
            f"SDK key is required to initialize {brand}. Please provide the sdk_key in the options.",
            None,
        )
        return None

    if not options or "account_id" not in options or not options["account_id"]:
        print(
            f"Account ID is required to initialize {brand}. Please provide the account_id in the options.",
            None,
        )
        return None

    if options.get("is_aliasing_enabled", False) and (
        not options.get("gateway_service", None)
        or not options.get("gateway_service", None).get("url")
    ):
        print(
            "Gateway service URL is required when aliasing is enabled. Please provide the gateway_service in the options.",
            None,
        )
        return None

    try:
        instance = Wingify.set_instance(options)
        sdk_init_time = int((time.time() * 1000) - start_time_for_init)

        was_initialized = False
        if getattr(instance, '_settings', None) is not None:
            sdk_meta_info = instance._settings.get_sdk_meta_info()
            if sdk_meta_info:
                was_initialized = sdk_meta_info.get("wasInitializedEarlier", False)

        if instance.is_settings_valid_on_init and not was_initialized:
            send_sdk_init_event(instance.settings_fetch_time, sdk_init_time)

        usage_stats_account_id = None
        if getattr(instance, '_settings', None) is not None:
            usage_stats_account_id = instance._settings.get_usage_stats_account_id()

        if usage_stats_account_id:
            sampling_service = InternalEventsSamplingService()
            if sampling_service.should_send_usage_stats_event(instance._settings):
                send_sdk_usage_stats_event(usage_stats_account_id)

        return instance
    except Exception as e:
        print(f"{brand} initialization failed. Error:", e)
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
        if not is_string(user_id) or user_id == "":
            print(f"userId passed to {api_name} API is not of valid type.")
            return None

        if not is_string(account_id) or account_id == "":
            print(f"accountId passed to {api_name} API is not of valid type.")
            return None

        return uuid_util_get_uuid(user_id, account_id)

    except Exception as error:
        print(f"API - {api_name} failed to execute. Trace: {error}")
        return None
