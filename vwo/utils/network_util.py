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


from typing import Any, Dict, Optional
import json
import random
from ..constants.Constants import Constants
from ..utils.uuid_util import get_uuid
from ..utils.data_type_util import is_object
from ..utils.function_util import get_current_unix_timestamp, get_current_unix_timestamp_in_millis, get_random_number
from ..packages.logger.core.log_manager import LogManager
from ..services.url_service import UrlService
from ..enums.url_enum import UrlEnum
from ..models.settings.settings_model import SettingsModel
from ..utils.log_message_util import debug_messages, error_messages
from ..packages.network_layer.manager.network_manager import NetworkManager
from ..packages.network_layer.models.request_model import RequestModel
from ..enums.headers_enum import HeadersEnum
import asyncio
import threading

def get_settings_path(sdk_key: str, account_id: str) -> Dict[str, Any]:
    path = {
        'i': sdk_key,              # Inject API key
        'r': random.random(),      # Random number for cache busting
        'a': account_id            # Account ID
    }
    return path

# Function to construct tracking path for an event
def get_track_event_path(event: str, account_id: str, user_id: str) -> Dict[str, Any]:
    return {
        'event_type': event,
        'account_id': account_id,
        'uId': user_id,
        'u': get_uuid(user_id, account_id),
        'sdk': Constants.SDK_NAME,
        'sdk-v': Constants.SDK_VERSION,
        'random': get_random_number(),
        'ap': Constants.AP,
        'sId': get_current_unix_timestamp(),
        'ed': json.dumps({'p': 'server'})
    }

# Function to construct query parameters for event batching
def get_event_batching_query_params(account_id: str) -> Dict[str, Any]:
    return {
        'a': account_id,
        'sd': Constants.SDK_NAME,
        'sv': Constants.SDK_VERSION
    }

# Function to build generic properties for tracking events
def get_events_base_properties(
    setting: SettingsModel,
    event_name: str,
    visitor_user_agent: str = '',
    ip_address: str = ''
) -> Dict[str, Any]:
    sdk_key = setting.get_sdk_key()
    return {
        'en': event_name,
        'a': setting.get_account_id(),
        'env': sdk_key,
        'eTime': get_current_unix_timestamp_in_millis(),
        'random': get_random_number(),
        'p': 'FS',
        'visitor_ua': visitor_user_agent,
        'visitor_ip': ip_address,
        'url': Constants.HTTPS_PROTOCOL + UrlService.get_base_url() + UrlEnum.EVENTS.value
    }

# Function to build payload for tracking events
def _get_event_base_payload(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    visitor_user_agent: str = '',
    ip_address: str = ''
) -> Dict[str, Any]:
    uuid_value = get_uuid(user_id, settings.get_account_id())
    sdk_key = settings.get_sdk_key()
    properties = {
        'd': {
            'msgId': f"{uuid_value}-{get_current_unix_timestamp_in_millis()}",
            'visId': uuid_value,
            'sessionId': get_current_unix_timestamp(),
            'visitor_ua': visitor_user_agent,
            'visitor_ip': ip_address,
            'event': {
                'props': {
                    'vwo_sdkName': Constants.SDK_NAME,
                    'vwo_sdkVersion': Constants.SDK_VERSION,
                    'vwo_envKey': sdk_key
                },
                'name': event_name,
                'time': get_current_unix_timestamp_in_millis()
            },
            'visitor': {
                'props': {
                    Constants.VWO_FS_ENVIRONMENT: sdk_key
                }
            }
        }
    }
    
    return properties

# Function to build payload for tracking user data
def get_track_user_payload_data(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    campaign_id: int,
    variation_id: int,
    visitor_user_agent: str = '',
    ip_address: str = ''
) -> Dict[str, Any]:
    properties = _get_event_base_payload(settings, user_id, event_name, visitor_user_agent, ip_address)
    
    properties['d']['event']['props']['id'] = campaign_id
    properties['d']['event']['props']['variation'] = str(variation_id)
    properties['d']['event']['props']['isFirst'] = 1
    
    LogManager.get_instance().debug(debug_messages.get('IMPRESSION_FOR_TRACK_USER').format(
        accountId = settings.get_account_id(),
        userId = user_id,
        campaignId = campaign_id
    ))
    
    return properties

# Function to build payload for tracking goals with custom event properties
def get_track_goal_payload_data(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    event_properties: Dict[str, Any],
    visitor_user_agent: str = '',
    ip_address: str = ''
) -> Dict[str, Any]:
    properties = _get_event_base_payload(settings, user_id, event_name, visitor_user_agent, ip_address)
    
    properties['d']['event']['props']['isCustomEvent'] = True
    properties['d']['event']['props']['variation'] = 1  # Temporary value for variation
    properties['d']['event']['props']['id'] = 1  # Temporary value for ID
    
    if event_properties and is_object(event_properties):
        for prop, value in event_properties.items():
            properties['d']['event']['props'][prop] = value
    
    LogManager.get_instance().debug(debug_messages.get('IMPRESSION_FOR_TRACK_GOAL').format(
        eventName = event_name,
        accountId = settings.get_account_id(),
        userId = user_id
    ))
    
    return properties

# Function to build payload for syncing visitor attributes
def get_attribute_payload_data(
    settings: SettingsModel,
    user_id: str,
    event_name: str,
    attribute_key: str,
    attribute_value: Any,
    visitor_user_agent: str = '',
    ip_address: str = ''
) -> Dict[str, Any]:
    properties = _get_event_base_payload(settings, user_id, event_name, visitor_user_agent, ip_address)
    
    properties['d']['event']['props']['isCustomEvent'] = True
    properties['d']['event']['props'][Constants.VWO_FS_ENVIRONMENT] = settings.get_sdk_key()
    properties['d']['visitor']['props'][attribute_key] = attribute_value
    
    LogManager.get_instance().debug(debug_messages.get('IMPRESSION_FOR_SYNC_VISITOR_PROP').format(
        eventName = event_name,
        accountId = settings.get_account_id(),
        userId = user_id
    ))
    
    return properties

# Function to send a POST API request
def send_post_api_request(properties: Dict[str, Any], payload: Dict[str, Any]):
    url = f"{Constants.HTTPS_PROTOCOL}://{UrlService.get_base_url()}{UrlEnum.EVENTS.value}"
    from ..services.settings_manager import SettingsManager

    headers = {
        HeadersEnum.USER_AGENT.value: payload['d'].get('visitor_ua', ''),
        HeadersEnum.IP.value: payload['d'].get('visitor_ip', '')
    }

    try:
        network_instance = NetworkManager.get_instance()
        request = RequestModel(
            UrlService.get_base_url(),
            'POST',
            UrlEnum.EVENTS.value,
            properties,
            payload,
            headers,
            SettingsManager.get_instance().protocol,
            SettingsManager.get_instance().port
        )

        # Attempt to get the running loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If an event loop is running, schedule the task safely
            asyncio.run_coroutine_threadsafe(network_instance.post_async(request), loop)
        else:
            # If no event loop is running, run it in a new detached thread
            run_in_thread(network_instance.post_async(request))
        
        return
    
    except Exception as err:
        LogManager.get_instance().error(
            error_messages.get('NETWORK_CALL_FAILED').format(
                method = 'POST',
                err = err,
            ),
        )

# Function to run an asyncio event loop in a separate thread
def run_in_thread(coro):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coro)
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    thread = threading.Thread(target=run)
    thread.daemon = True  # Ensure the thread does not block program exit
    thread.start()