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


from typing import Any, Dict, Optional
import json
import random
from ..constants.Constants import Constants
from ..utils.uuid_util import get_uuid
from ..utils.data_type_util import is_object
from ..utils.function_util import (
    get_current_unix_timestamp,
    get_current_unix_timestamp_in_millis,
    get_random_number,
)
from ..packages.logger.core.log_manager import LogManager
from ..services.url_service import UrlService
from ..enums.url_enum import UrlEnum
from ..models.settings.settings_model import SettingsModel
from ..utils.log_message_util import debug_messages, error_messages, info_messages
from ..packages.network_layer.manager.network_manager import NetworkManager
from ..packages.network_layer.models.request_model import RequestModel
from ..enums.headers_enum import HeadersEnum
from ..utils.usage_stats_util import UsageStatsUtil
from ..services.settings_manager import SettingsManager
from ..enums.event_enum import EventEnum

# Function to construct tracking path for an event
def get_track_event_path(event: str, account_id: str, user_id: str) -> Dict[str, Any]:
    return {
        "event_type": event,
        "account_id": account_id,
        "uId": user_id,
        "u": get_uuid(user_id, account_id),
        "sdk": Constants.SDK_NAME,
        "sdk-v": Constants.SDK_VERSION,
        "random": get_random_number(),
        "ap": Constants.AP,
        "sId": get_current_unix_timestamp(),
        "ed": json.dumps({"p": "server"}),
    }


# Function to construct query parameters for event batching
def get_event_batching_query_params(account_id: str) -> Dict[str, Any]:
    return {"a": account_id, "sd": Constants.SDK_NAME, "sv": Constants.SDK_VERSION}


# Function to build generic properties for tracking events
def get_events_base_properties(
    event_name: str, visitor_user_agent: str = "", ip_address: str = "", is_usage_stats_event: bool = False, usage_stats_account_id: int = None
) -> Dict[str, Any]:

    # Get the instance of SettingsManager
    settings = SettingsManager.get_instance()

    # Fetch SDK key and account ID from the SettingsManager instance
    sdk_key = settings.get_sdk_key()
    account_id = settings.get_account_id()

    properties = {
        "en": event_name,
        "a": account_id,
        "eTime": get_current_unix_timestamp_in_millis(),
        "random": get_random_number(),
        "p": "FS",
        "visitor_ua": visitor_user_agent,
        "visitor_ip": ip_address,
        "url": Constants.HTTPS_PROTOCOL
        + UrlService.get_base_url()
        + UrlEnum.EVENTS.value,
    }

    if not is_usage_stats_event:
        # set env key for standard sdk events
        properties["env"] = sdk_key
    else:
        # set account id for internal usage stats event
        properties["a"] = str(usage_stats_account_id)
    return properties


# Function to build payload for tracking events
def _get_event_base_payload(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    visitor_user_agent: str = "",
    ip_address: str = "",
    is_usage_stats_event: bool = False,
    usage_stats_account_id: int = None,
) -> Dict[str, Any]:

    account_id = SettingsManager.get_instance().get_account_id()
    if is_usage_stats_event:
        # set account id for internal usage stats event
        account_id = usage_stats_account_id

    uuid_value = get_uuid(str(user_id), str(account_id))
    sdk_key = SettingsManager.get_instance().get_sdk_key()

    props = {
        "vwo_sdkName": Constants.SDK_NAME,
        "vwo_sdkVersion": Constants.SDK_VERSION,
    }

    if not is_usage_stats_event:
        # set env key for standard sdk events
        props["vwo_envKey"] = sdk_key

    properties = {
        "d": {
            "msgId": f"{uuid_value}-{get_current_unix_timestamp_in_millis()}",
            "visId": uuid_value,
            "sessionId": get_current_unix_timestamp(),
            "visitor_ua": visitor_user_agent,
            "visitor_ip": ip_address,
            "event": {
                "props": props,
                "name": event_name,
                "time": get_current_unix_timestamp_in_millis(),
            },
        }
    }

    if not is_usage_stats_event:
        # set visitor props for standard sdk events
        properties["d"]["visitor"] = {
            "props": {
                Constants.VWO_FS_ENVIRONMENT: sdk_key,
            },
        }

    return properties


# Function to build payload for tracking user data
def get_track_user_payload_data(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    campaign_id: int,
    variation_id: int,
    visitor_user_agent: str = "",
    ip_address: str = "",
) -> Dict[str, Any]:
    properties = _get_event_base_payload(
        settings, user_id, event_name, visitor_user_agent, ip_address
    )

    properties["d"]["event"]["props"]["id"] = campaign_id
    properties["d"]["event"]["props"]["variation"] = str(variation_id)
    properties["d"]["event"]["props"]["isFirst"] = 1

    LogManager.get_instance().debug(
        debug_messages.get("IMPRESSION_FOR_TRACK_USER").format(
            accountId=settings.get_account_id(), userId=user_id, campaignId=campaign_id
        )
    )

    return properties


# Function to build payload for tracking goals with custom event properties
def get_track_goal_payload_data(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    event_properties: Dict[str, Any],
    visitor_user_agent: str = "",
    ip_address: str = "",
) -> Dict[str, Any]:
    properties = _get_event_base_payload(
        settings, user_id, event_name, visitor_user_agent, ip_address
    )

    properties["d"]["event"]["props"]["isCustomEvent"] = True
    properties["d"]["event"]["props"]["variation"] = 1  # Temporary value for variation
    properties["d"]["event"]["props"]["id"] = 1  # Temporary value for ID

    if event_properties and is_object(event_properties):
        for prop, value in event_properties.items():
            properties["d"]["event"]["props"][prop] = value

    LogManager.get_instance().debug(
        debug_messages.get("IMPRESSION_FOR_TRACK_GOAL").format(
            eventName=event_name, accountId=settings.get_account_id(), userId=user_id
        )
    )

    return properties


# Function to build payload for syncing visitor attributes
def get_attribute_payload_data(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    attribute_map: Dict,
    visitor_user_agent: str = "",
    ip_address: str = "",
) -> Dict[str, Any]:
    properties = _get_event_base_payload(
        settings, user_id, event_name, visitor_user_agent, ip_address
    )

    properties["d"]["event"]["props"]["isCustomEvent"] = True
    properties["d"]["event"]["props"][
        Constants.VWO_FS_ENVIRONMENT
    ] = settings.get_sdk_key()
    properties["d"]["visitor"]["props"].update(attribute_map)

    LogManager.get_instance().debug(
        debug_messages.get("IMPRESSION_FOR_SYNC_VISITOR_PROP").format(
            eventName=event_name, accountId=settings.get_account_id(), userId=user_id
        )
    )

    return properties


# Function to send a POST API request without waiting for the response
def send_post_api_request(
    properties: Dict[str, Any], payload: Dict[str, Any], user_id: str
):
    try:
        # Initialize the headers dictionary for the request
        headers = {}

        # Retrieve 'visitor_ua' and 'visitor_ip' from the payload if they exist
        visitor_ua = payload["d"].get("visitor_ua")
        visitor_ip = payload["d"].get("visitor_ip")

        # Add headers if they exist
        if visitor_ua and isinstance(visitor_ua, str) and visitor_ua.strip():
            headers[HeadersEnum.USER_AGENT.value] = visitor_ua.strip()
        if visitor_ip and isinstance(visitor_ip, str) and visitor_ip.strip():
            headers[HeadersEnum.IP.value] = visitor_ip.strip()

        # Create the request model
        request = RequestModel(
            UrlService.get_base_url(),
            "POST",
            UrlEnum.EVENTS.value,
            properties,
            payload,
            headers,
            SettingsManager.get_instance().protocol,
            SettingsManager.get_instance().port,
        )

        # Will be used for logging purpose inside post_async method
        request.set_user_id(user_id)

        # Get network instance
        network_instance = NetworkManager.get_instance()

        # Create a background thread to send the request
        def send_request():
            try:
                response = network_instance.post(request)
                if response.status_code == 200:
                    # clear the usage stats data
                    UsageStatsUtil().clear_usage_stats()
                    
                    request_query = request.get_query()
                    LogManager.get_instance().info(
                        info_messages.get("NETWORK_CALL_SUCCESS").format(
                            event=request_query.get("en"),
                            endPoint=request.get_url().split("?")[0],
                            accountId=request_query.get("a"),
                            userId=request.get_user_id(),
                            uuid=request.get_body().get("d").get("visId"),
                        )
                    )
            except Exception as e:
                LogManager.get_instance().error(
                    error_messages.get("NETWORK_CALL_FAILED").format(
                        method="POST",
                        err=str(e),
                    ),
                )

        # Start the request in a background thread if threading is enabled
        if network_instance.should_use_threading:
            network_instance.execute_in_background(send_request)
        else:
            send_request()

    except Exception as err:
        LogManager.get_instance().error(
            error_messages.get("NETWORK_CALL_FAILED").format(
                method="POST",
                err=err,
            ),
        )


def send_post_batch_request(
    payload: dict, account_id: int, sdk_key: str, flush_callback=None
):

    try:
        # Prepare the batch payload
        batch_payload = {"ev": payload}

        # Prepare query parameters
        query = {"a": str(account_id), "env": sdk_key}

        # Create the RequestModel with necessary data
        request_model = RequestModel(
            UrlService.get_base_url(),
            "POST",
            UrlEnum.BATCH_EVENTS.value,
            query,
            batch_payload,
            {
                "Authorization": sdk_key,
                "Content-Type": "application/json",
            },
            SettingsManager.get_instance().protocol,
            SettingsManager.get_instance().port,
        )

        request_model.set_user_id("NA")
        # Call PostAsync to send the request asynchronously
        network_manager = NetworkManager.get_instance()
        response = network_manager.post(request_model)

        # After sending the request, check the response
        if response.status_code == 200:
            # On success, call the flush callback if defined
            if flush_callback:
                flush_callback(None, payload)  # No error, events sent successfully
            return True
        else:
            # On failure, call the flush callback with error
            if flush_callback:
                flush_callback(
                    f"Failed with status code: {response.status_code}", payload
                )
            return False
    except Exception as ex:
        LogManager.get_instance().error(
            f"Error occurred while sending batch events: {ex}"
        )

        # Call flush callback with error
        if flush_callback:
            flush_callback(str(ex), payload)
        return False


# Function to construct the messaging event payload
def get_messaging_event_payload(
    message_type: str, message: str, event_name: str
) -> Dict[str, Any]:
    # Get user ID and properties
    settings = SettingsManager.get_instance()
    user_id = f"{settings.get_account_id()}_{settings.get_sdk_key()}"
    properties = _get_event_base_payload(None, user_id, event_name, None, None)

    # Set the environment key and product
    properties["d"]["event"]["props"]["vwo_envKey"] = settings.get_sdk_key()
    properties["d"]["event"]["props"][
        "product"
    ] = Constants.PRODUCT_NAME

    # Set the message data
    data = {
        "type": message_type,
        "content": {
            "title": message,
            "dateTime": get_current_unix_timestamp_in_millis(),
        },
    }

    # Add data to the properties
    properties["d"]["event"]["props"]["data"] = data

    return properties


def get_sdk_init_event_payload(
    event_name: str,
    settings_fetch_time: Optional[int] = None,
    sdk_init_time: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Constructs the payload for sdk init called event.
    
    Args:
        event_name: The name of the event.
        settings_fetch_time: Time taken to fetch settings in milliseconds.
        sdk_init_time: Time taken to initialize the SDK in milliseconds.
        
    Returns:
        The constructed payload with required fields.
    """
    # Get user ID and properties
    settings = SettingsManager.get_instance()
    user_id = f"{settings.get_account_id()}_{settings.get_sdk_key()}"
    properties = _get_event_base_payload(None, user_id, event_name, None, None)

    # Set the required fields as specified
    properties["d"]["event"]["props"][Constants.VWO_FS_ENVIRONMENT] = settings.get_sdk_key()
    properties["d"]["event"]["props"]["product"] = Constants.PRODUCT_NAME
    
    data = {
        "isSDKInitialized": True,
        "settingsFetchTime": settings_fetch_time,
        "sdkInitTime": sdk_init_time,
    }
    properties["d"]["event"]["props"]["data"] = data

    return properties


def get_sdk_usage_stats_event_payload(
    event_name: str, usage_stats_account_id: int
) -> Dict[str, Any]:
    """
    Constructs the payload for sdk usage stats event.
    
    Args:
        event_name: The name of the event.
        usage_stats_account_id: Account ID for usage stats event.
        
    Returns:
        The constructed payload with required fields.
    """
    # Get user ID and properties
    settings = SettingsManager.get_instance()
    user_id = f"{settings.get_account_id()}_{settings.get_sdk_key()}"
    properties = _get_event_base_payload(None, user_id, event_name, None, None, True, usage_stats_account_id)

    # Set the required fields as specified
    properties["d"]["event"]["props"]["product"] = Constants.PRODUCT_NAME
    properties["d"]["event"]["props"]["vwoMeta"] = UsageStatsUtil().get_usage_stats()

    return properties


def send_event(
    properties: Dict[str, Any], payload: Dict[str, Any], event_name: str
) -> Dict[str, Any]:
    try:
        #if event_name is not VWO_LOG_EVENT, then set base url to constants.hostname
        if event_name == EventEnum.VWO_LOG_EVENT.value or event_name == EventEnum.VWO_USAGE_STATS.value:
            base_url = Constants.HOST_NAME
            protocol = Constants.HTTPS_PROTOCOL
            port = 443
        else:
            base_url = UrlService.get_base_url()
            protocol = SettingsManager.get_instance().protocol
            port = SettingsManager.get_instance().port

        # Create the request model
        request = RequestModel(
            base_url,
            "POST",
            UrlEnum.EVENTS.value,
            properties,
            payload,
            None,
            protocol,
            port,
        )

        # Get network instance
        network_instance = NetworkManager.get_instance()

        # Create a background thread to send the request
        def send_request():
            try:
                network_instance.post(request)
            except Exception:
                pass

        # Start the request in a background thread if threading is enabled
        if network_instance.should_use_threading:
            network_instance.execute_in_background(send_request)
        else:
            send_request()

        return {"success": True, "message": "Event sent successfully"}

    except Exception:
        return {"success": False, "message": "Failed to send event"}
