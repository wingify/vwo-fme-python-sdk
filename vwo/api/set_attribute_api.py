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
from typing import Dict, Any
from ..models.settings.settings_model import SettingsModel
from ..models.user.context_model import ContextModel
from ..utils.network_util import (
    get_events_base_properties,
    get_attribute_payload_data,
    send_post_api_request,
)
from ..enums.event_enum import EventEnum


class SetAttributeApi:
    def set_attribute(
        self, settings: SettingsModel, attribute_map: Dict, context: ContextModel
    ):
        self.create_and_send_impression_for_attribute(settings, attribute_map, context)

    def create_and_send_impression_for_attribute(
        self, settings: SettingsModel, attribute_map: Dict, context: ContextModel
    ):
        properties = get_events_base_properties(
            EventEnum.VWO_SYNC_VISITOR_PROP.value,
            visitor_user_agent=context.get_user_agent(),
            ip_address=context.get_ip_address(),
        )
        # Construct payload data for tracking the goal
        payload = get_attribute_payload_data(
            settings,
            context.get_id(),
            EventEnum.VWO_SYNC_VISITOR_PROP.value,
            attribute_map,
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