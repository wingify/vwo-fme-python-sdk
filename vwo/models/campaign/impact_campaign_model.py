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

from typing import Dict


class ImpactCampaignModel:
    def __init__(self, data: Dict):
        """
        Initialize the ImpactCampaignModel with the provided data dictionary.

        :param data: A dictionary containing the campaign ID and type.
        """
        self._campaign_id = data.get("campaignId", None)
        self._type = data.get("type", None)

    # Getter methods for accessing private attributes
    def get_campaign_id(self) -> int:
        """
        Get the campaign ID.

        :return: The campaign ID as an integer.
        """
        return self._campaign_id

    def get_type(self) -> str:
        """
        Get the type of the campaign.

        :return: The type as a string.
        """
        return self._type

    # Setter methods for modifying the attributes
    def set_campaign_id(self, value: int):
        """
        Set the campaign ID.

        :param value: The new campaign ID as an integer.
        """
        self._campaign_id = value

    def set_type(self, value: str):
        """
        Set the type of the campaign.

        :param value: The new type as a string.
        """
        self._type = value
