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
from .network_util import get_events_base_properties, get_sdk_init_event_payload, get_sdk_usage_stats_event_payload, send_event
from ..enums.event_enum import EventEnum
from ..vwo_client import VWOClient
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import error_messages

def send_sdk_init_event(settings_fetch_time: Optional[int] = None, sdk_init_time: Optional[int] = None) -> None:
    """
    Sends an init called event to VWO.
    This event is triggered when the init function is called.
    
    :param settings_fetch_time: Time taken to fetch settings in milliseconds
    :param sdk_init_time: Time taken to initialize the SDK in milliseconds
    """
    # Create the query parameters
    properties = get_events_base_properties(EventEnum.VWO_SDK_INIT_EVENT.value)
    
    # Create the payload with required fields
    payload = get_sdk_init_event_payload(EventEnum.VWO_SDK_INIT_EVENT.value, settings_fetch_time, sdk_init_time)
    
    # Send the constructed payload via POST request
    try:
        vwo_instance = VWOClient.get_instance()

        # Check if batch events are enabled
        if vwo_instance.batch_event_queue is not None:
            # Enqueue the event to the batch queue
            vwo_instance.batch_event_queue.enqueue(payload)
        else:
            # Send the event immediately if batch events are not enabled
            send_event(properties, payload, EventEnum.VWO_SDK_INIT_EVENT.value)
    except Exception as e:
        LogManager.get_instance().error(
            error_messages.get("SDK_INIT_EVENT_FAILED").format(
                err=str(e)
            )
        )
        pass


def send_sdk_usage_stats_event(usage_stats_account_id: int) -> None:
    """
    Sends a usage stats event to VWO.
    This event is triggered when the SDK is initialized.
    
    :param usage_stats_account_id: Account ID for usage stats event
    """
    # Create the query parameters
    properties = get_events_base_properties(EventEnum.VWO_USAGE_STATS.value, "", "", True, usage_stats_account_id)

    # Create the payload with required fields
    payload = get_sdk_usage_stats_event_payload(EventEnum.VWO_USAGE_STATS.value, usage_stats_account_id)

    vwo_instance = VWOClient.get_instance()

    # Check if batch events are enabled
    if vwo_instance.batch_event_queue is not None and vwo_instance.batch_event_queue.is_enabled():
        # Enqueue the event to the batch queue
        vwo_instance.batch_event_queue.enqueue(payload)
    else:
        # Send the event immediately if batch events are not enabled
        send_event(properties, payload, EventEnum.VWO_USAGE_STATS.value)
    