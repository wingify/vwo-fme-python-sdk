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
from ..utils.network_util import (
    get_events_base_properties,
    get_track_user_payload_data,
    send_post_api_request,
)
from ..enums.event_enum import EventEnum
from ..utils.campaign_util import (
    get_campaign_key_from_campaign_id,
    get_variation_name_from_campaign_id_and_variation_id,
    get_campaign_type_from_campaign_id,
)
from ..constants.Constants import Constants


# The function that creates and sends an impression for a variation shown event
def create_and_send_impression_for_variation_shown(
    settings: SettingsModel, campaign_id: int, variation_id: int, context: ContextModel, feature_key: str
):
    from ..vwo_client import VWOClient
    # Get base properties for the event
    properties = get_events_base_properties(
        EventEnum.VWO_VARIATION_SHOWN.value,
        visitor_user_agent=context.get_user_agent(),
        ip_address=context.get_ip_address(),
    )
    # Construct payload data for tracking the user
    payload = get_track_user_payload_data(
        settings,
        EventEnum.VWO_VARIATION_SHOWN.value,
        campaign_id,
        variation_id,
        context,
    )

    campaign_key_with_feaure_key = get_campaign_key_from_campaign_id(settings, campaign_id)
    variation_name = get_variation_name_from_campaign_id_and_variation_id(settings, campaign_id, variation_id)
    campaign_type = get_campaign_type_from_campaign_id(settings, campaign_id)
    campaign_key = None
    if feature_key == campaign_key_with_feaure_key:
        campaign_key = Constants.IMPACT_ANALYSIS
    else:
        feature_key_with_underscore = feature_key + "_"
        campaign_key = campaign_key_with_feaure_key.split(feature_key_with_underscore)[1]

    vwo_instance = VWOClient.get_instance()

    # Check if batch events are enabled
    if vwo_instance.batch_event_queue is not None:
        # Enqueue the event to the batch queue
        vwo_instance.batch_event_queue.enqueue(payload)
    else:
        # Send the event immediately if batch events are not enabled
        send_post_api_request(properties, payload, context.get_id(), feature_info={
            "campaign_key": campaign_key,
            "variation_name": variation_name,
            "campaign_type": campaign_type,
            "feature_key": feature_key,
        })