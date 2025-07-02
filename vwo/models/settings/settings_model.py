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


from typing import List, Dict, Optional
from ..campaign.campaign_model import CampaignModel
from ..campaign.feature_model import FeatureModel
from ...utils.model_utils import _parse_campaign, _parse_feature
import json
from ...constants.Constants import Constants


class SettingsModel:
    def __init__(self, data: Dict):
        # Parse and set attributes
        self._features = [_parse_feature(f) for f in data["features"]]
        self._account_id = data["accountId"]
        self._groups = data.get("groups", {})
        self._campaign_groups = data.get("campaignGroups", {})
        self._campaigns = [_parse_campaign(c) for c in data["campaigns"]]
        self._sdk_key = data["sdkKey"]
        self._version = data["version"]
        self._collection_prefix = data.get("collectionPrefix", None)
        self._poll_interval = data.get("pollInterval", Constants.POLLING_INTERVAL)

    # Getter methods for accessing private attributes
    def get_features(self) -> List[FeatureModel]:
        return self._features

    def get_account_id(self) -> int:
        return self._account_id

    def get_groups(self) -> Optional[Dict]:
        return self._groups

    def get_campaign_groups(self) -> Optional[Dict[str, int]]:
        return self._campaign_groups

    def get_campaigns(self) -> List[CampaignModel]:
        return self._campaigns

    def get_sdk_key(self) -> str:
        return self._sdk_key

    def get_version(self) -> int:
        return self._version

    def get_collection_prefix(self) -> Optional[str]:
        return self._collection_prefix

    # Setter methods for modifying private attributes
    def set_features(self, value: List[FeatureModel]):
        self._features = value

    def set_account_id(self, value: int):
        self._account_id = value

    def set_groups(self, value: Dict):
        self._groups = value

    def set_campaign_groups(self, value: Dict[str, int]):
        self._campaign_groups = value

    def set_campaigns(self, value: List[CampaignModel]):
        self._campaigns = value

    def set_sdk_key(self, value: str):
        self._sdk_key = value

    def set_version(self, value: int):
        self._version = value

    def set_collection_prefix(self, value: Optional[str]):
        self._collection_prefix = value

    def set_poll_interval(self, value: int):
        self._poll_interval = value

    def get_poll_interval(self) -> int:
        return self._poll_interval