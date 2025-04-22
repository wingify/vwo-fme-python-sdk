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


from typing import Any, Dict
from ..packages.network_layer.manager.network_manager import NetworkManager
from ..services.settings_manager import SettingsManager
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import error_messages
from ..packages.network_layer.models.request_model import RequestModel
from ..services.url_service import UrlService
from urllib.parse import urlencode
import json
import re
from ..models.settings.settings_model import SettingsModel
from ..enums.campaign_type_enum import CampaignTypeEnum


def get_from_gateway_service(query_params: Dict[str, Any], endpoint: str) -> Any:
    network_instance = NetworkManager.get_instance()

    # Check if the base URL is correctly set
    if not SettingsManager.get_instance().is_gateway_service_provided:
        LogManager.get_instance().error(error_messages.get("GATEWAY_URL_ERROR"))
        return False

    try:
        # Create a new request model instance with the provided parameters
        request = RequestModel(
            url=UrlService.get_base_url(),
            method="GET",
            path=endpoint,
            query=query_params,
            scheme=SettingsManager.get_instance().protocol,
            port=SettingsManager.get_instance().port,
        )

        # Perform the network GET request synchronously
        response = network_instance.get(request)

        # Return the data from the response
        return response.get_data() if response else False
    except Exception as e:
        LogManager.get_instance().error(str(e))
        return False


def get_query_params(query_params: Dict[str, Any]) -> Dict[str, str]:
    encoded_params = {
        key: urlencode({key: str(value)})[len(key) + 1 :]
        for key, value in query_params.items()
    }
    return encoded_params


def add_is_gateway_service_required_flag(settings: SettingsModel) -> None:
    # Regex pattern to match the specified fields
    main_pattern = re.compile(
        r"\b(country|region|city|os|device_type|browser_string|ua)\b", re.IGNORECASE
    )
    # Regex pattern to match inlist(...) under custom_variable
    custom_variable_pattern = re.compile(r"inlist\([^)]*\)", re.IGNORECASE)

    for feature in settings.get_features():
        rules = feature.get_rules_linked_campaign()
        for rule in rules:
            segments = {}
            if rule.get_type() in [
                CampaignTypeEnum.PERSONALIZE.value,
                CampaignTypeEnum.ROLLOUT.value,
            ]:
                segments = rule.get_variations()[0].get_segments()
            else:
                segments = rule.get_segments()

            if segments:
                json_segments = json.dumps(segments)

                # Check if the json_segments contain the specified fields
                matches = main_pattern.findall(json_segments)

                # Check if json_segments contain "custom_variable"
                if '"custom_variable"' in json_segments:
                    custom_matches = custom_variable_pattern.findall(json_segments)
                else:
                    custom_matches = []

                # If there are matches in either the main or custom variable patterns, set the flag
                if matches or custom_matches:
                    feature.set_is_gateway_service_required(True)
                    break
