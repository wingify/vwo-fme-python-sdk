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


from ..models.settings.settings_model import SettingsModel
from ..models.user.context_model import ContextModel
from ..models.user.context_model import ContextModel
from ..services.hooks_manager import HooksManager
from ..packages.logger.core.log_manager import LogManager
from typing import Dict, Any
from ..utils.function_util import does_event_belong_to_any_feature
from ..models.settings.settings_model import SettingsModel
from ..models.user.context_model import ContextModel
from ..utils.network_util import (
    get_events_base_properties,
    get_track_goal_payload_data,
    send_post_api_request,
)
from ..enums.api_enum import ApiEnum
from ..utils.log_message_util import error_messages


class TrackApi:
    def track(
        self,
        settings: SettingsModel,
        event_name: str,
        context: ContextModel,
        event_properties: Dict[str, Any],
        hook_manager: HooksManager,
    ) -> Dict:
        """
        Tracks an event with given properties and context.
        Checks if the event exists, creates an impression, and executes hooks.

        :param settings: The settings file containing the account settings.
        :param event_name: The name of the event to track.
        :param event_properties: The properties of the event.
        :param context: The context of the user.
        :param hook_manager: The hook manager to execute hooks.
        """
        if does_event_belong_to_any_feature(event_name, settings):
            self.create_and_send_impression_for_track(
                settings, event_name, context, event_properties
            )
            hook_manager.set({"event_name": event_name, "api": ApiEnum.TRACK.value})
            hook_manager.execute(hook_manager.get())
            return {event_name: True}

        LogManager.get_instance().error(
            error_messages.get("EVENT_NOT_FOUND").format(eventName=event_name)
        )
        return {event_name: False}

    def create_and_send_impression_for_track(
        self,
        settings: SettingsModel,
        event_name: str,
        context: ContextModel,
        event_properties: Dict[str, Any],
    ):
        """
        Creates an impression for a track event and sends it via a POST API request.

        :param settings: The settings file containing the account settings.
        :param event_name: The name of the event to track.
        :param context: The context of the user.
        :param event_properties: The properties of the event.
        """
        properties = get_events_base_properties(
            event_name,
            visitor_user_agent=context.get_user_agent(),
            ip_address=context.get_ip_address(),
        )
        # Construct payload data for tracking the goal
        payload = get_track_goal_payload_data(
            settings,
            context.get_id(),
            event_name,
            event_properties,
            visitor_user_agent=context.get_user_agent(),
            ip_address=context.get_ip_address(),
        )

        from vwo.vwo_client import VWOClient
        vwo_instance = VWOClient.get_instance()

        # Check if batch events are enabled
        if vwo_instance.batch_event_queue is not None:
            # Enqueue the event to the batch queue
            vwo_instance.batch_event_queue.enqueue(payload)
        else:
            # Send the event immediately if batch events are not enabled
            send_post_api_request(properties, payload, context.get_id())