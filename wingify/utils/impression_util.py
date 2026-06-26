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


from ..models.user.context_model import ContextModel
from ..utils.network_util import (
    get_events_base_properties,
    send_post_api_request,
    send_post_batch_request,
)
from ..enums.event_enum import EventEnum
from ..packages.network_layer.manager.network_manager import NetworkManager


# The function that creates and sends an impression for a variation shown event
def send_impression_for_variation_shown(payload: dict, context: ContextModel):
    """
    Sends an impression for a variation shown event.
    :param payload: The payload containing the event data
    :param context: The context of the user
    """
    from ..wingify_client import WingifyClient as VWOClient

    # Get base properties for the event
    properties = get_events_base_properties(
        EventEnum.VARIATION_SHOWN.value,
        visitor_user_agent=context.get_user_agent(),
        ip_address=context.get_ip_address(),
    )

    vwo_instance = VWOClient.get_instance()

    # Check if batch events are enabled
    if vwo_instance.batch_event_queue is not None:
        # Enqueue the event to the batch queue
        vwo_instance.batch_event_queue.enqueue(payload)
    else:
        # Send the event immediately if batch events are not enabled
        send_post_api_request(properties, payload, context.get_id())

def send_impression_for_variation_shown_batch(
    batch_payload: dict, account_id: int, sdk_key: str
):
    """
    Sends an impression for a variation shown event in batch.
    :param batch_payload: The batch payload containing all events from getFlag for a single user
    :param account_id: The account ID
    :param sdk_key: The SDK key
    """
    from ..wingify_client import WingifyClient as VWOClient

    vwo_instance = VWOClient.get_instance()
    if vwo_instance.batch_event_queue is not None:
        # batch_payload - contains all events from getFlag for a single user
        # add each event to the batch queue
        for payload in batch_payload:
            vwo_instance.batch_event_queue.enqueue(payload)
    else:
        # Send the batch events immediately if batch events are not enabled
        network_instance = NetworkManager.get_instance()

        # Create a method to send the request
        def send_batch_request():
            send_post_batch_request(batch_payload, account_id, sdk_key)

        # check if threading is enabled
        if network_instance.should_use_threading:
            # execute the request in a background thread
            network_instance.execute_in_background(send_batch_request)
        else:
            # execute the request immediately
            send_batch_request()


def create_and_send_impression_for_usage_tracking(
    settings, feature_key: str, context: ContextModel
):
    """
    Creates and sends an impression for usage tracking.
    
    This function is used to send a tracking event to the server when a feature flag
    is evaluated but no primary `variation_shown` event is dispatched (e.g., when serving
    cached decisions from storage, or when the flag is not found).
    
    :param settings: The settings file containing the account settings.
    :param feature_key: The feature key for which usage is being tracked.
    :param context: The ContextModel object containing user and session context.
    """
    from ..wingify_client import WingifyClient as VWOClient
    from ..utils.network_util import _get_event_base_payload
    from ..packages.logger.core.log_manager import LogManager
    from ..utils.log_message_util import debug_messages
    from ..utils.function_util import get_current_unix_timestamp_in_millis
    from ..utils.brand_util import get_sdk_name
    from ..services.settings_manager import SettingsManager

    user_id = context.get_id()

    properties = _get_event_base_payload(
        settings=settings,
        user_id=user_id,
        event_name=EventEnum.TRACK_USAGE.value,
        visitor_user_agent=context.get_user_agent(),
        ip_address=context.get_ip_address(),
    )

    if context.get_session_id() is not None and context.get_session_id() != 0:
        properties["d"]["sessionId"] = context.get_session_id()

    # if uuid is provided in the context, use it, otherwise generate a new one
    if context.get_vwo_uuid() is not None and context.get_vwo_uuid() != "":
        properties["d"]["msgId"] = f"{context.get_vwo_uuid()}-{get_current_unix_timestamp_in_millis()}"
        properties["d"]["visId"] = context.get_vwo_uuid()

    LogManager.get_instance().debug(
        debug_messages.get("IMPRESSION_FOR_TRACK_USAGE").format(
            brand=get_sdk_name(SettingsManager.get_instance().is_via_vwo),
            accountId=settings.get_account_id(),
            userId=user_id,
            featureKey=feature_key
        )
    )

    # Note: id, variation, isFirst are not set!

    vwo_instance = VWOClient.get_instance()
    
    # Get base properties for the event
    base_properties = get_events_base_properties(
        EventEnum.TRACK_USAGE.value,
        visitor_user_agent=context.get_user_agent(),
        ip_address=context.get_ip_address(),
    )

    if vwo_instance.batch_event_queue is not None:
        # Enqueue the event to the batch queue
        vwo_instance.batch_event_queue.enqueue(properties)
    else:
        # Send the event immediately if batch events are not enabled
        send_post_api_request(base_properties, properties, user_id)