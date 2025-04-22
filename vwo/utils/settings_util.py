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
from .campaign_util import set_variation_allocation
from .function_util import add_linked_campaigns_to_settings
from .gateway_service_util import add_is_gateway_service_required_flag
from typing import Any, Dict


def set_settings_and_add_campaigns_to_rules(
    settings: Dict, vwo_client_instance: Any
) -> None:
    # Initialize the settings model with the provided settings
    vwo_client_instance._settings = SettingsModel(settings)
    vwo_client_instance.original_settings = settings
    # Get the campaigns from the settings once and process each campaign
    campaigns = vwo_client_instance._settings.get_campaigns()
    for index, campaign in enumerate(campaigns):
        set_variation_allocation(campaign)
        campaigns[index] = (
            campaign  # Update the campaign back into the List (if necessary)
        )

    # Add linked campaigns to settings and set gateway service required flag
    add_linked_campaigns_to_settings(vwo_client_instance._settings)
    add_is_gateway_service_required_flag(vwo_client_instance._settings)
