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


from ..models.settings.settings_model import SettingsModel
from ..models.user.context_model import ContextModel
from ..models.user.context_model import ContextModel
from typing import Dict, Any
from ..models.settings.settings_model import SettingsModel
from ..models.user.context_model import ContextModel
from ..utils.network_util import get_events_base_properties, get_attribute_payload_data, send_post_api_request
from ..enums.event_enum import EventEnum

class SetAttributeApi:
    def set_attribute(self, settings: SettingsModel, attribute_key: str, attribute_value: Any, context: ContextModel):
        self.create_and_send_impression_for_attribute(settings, attribute_key, attribute_value, context)
    
    def create_and_send_impression_for_attribute(
        self,
        settings: SettingsModel,
        attribute_key: str,
        attribute_value: Any, 
        context: ContextModel
    ):
        properties = get_events_base_properties(
            settings,
            EventEnum.VWO_SYNC_VISITOR_PROP.value,
            visitor_user_agent=context.get_user_agent(),
            ip_address=context.get_ip_address()
        )
        # Construct payload data for tracking the goal
        payload = get_attribute_payload_data(
            settings,
            context.get_id(),
            EventEnum.VWO_SYNC_VISITOR_PROP.value,
            attribute_key,
            attribute_value,
            visitor_user_agent=context.get_user_agent(),
            ip_address=context.get_ip_address()
        )

        # Send the constructed properties and payload as a POST request
        send_post_api_request(properties, payload)
            