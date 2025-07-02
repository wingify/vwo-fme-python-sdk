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


from typing import List, Dict, Any, Optional
from .variation_model import VariationModel
from .variable_model import VariableModel
from .metric_model import MetricModel


class CampaignModel:
    def __init__(
        self,
        id: int,
        isForcedVariationEnabled: bool,
        segments: Dict[str, Any],
        variations: List[VariationModel],
        status: str,
        type: str,
        key: str,
        isAlwaysCheckSegment: bool,
        name: str,
        percentTraffic: Optional[int] = None,
        is_user_list_enabled: bool = False,
        metrics: List[Dict[str, Any]] = [],
        variables: List[Dict[str, Any]] = [],
        variation_id: int = None,
        campaign_id: int = None,
        rule_key: str = None,
        weight: float = 0,
        start_range_variation: float = None,
        end_range_variation: float = None,
        salt: str = None,
    ):
        self._id = id
        self._segments = segments
        self._percent_traffic = percentTraffic
        self.is_user_list_enabled = is_user_list_enabled
        self._key = key
        self._type = type
        self._name = name
        self._is_forced_variation_enabled = isForcedVariationEnabled
        self._variations = variations
        self._metrics = metrics
        self._variables = variables
        self._variation_id = variation_id
        self._campaign_id = campaign_id
        self._rule_key = rule_key
        self._status = status
        self._is_always_check_segment = isAlwaysCheckSegment
        self._weight = weight
        self._start_range_variation = start_range_variation
        self._end_range_variation = end_range_variation
        self._salt = salt

    def get_id(self) -> int:
        return self._id

    def get_is_forced_variation_enabled(self) -> bool:
        return self._is_forced_variation_enabled

    def get_segments(self) -> Dict[str, Any]:
        return self._segments

    def get_variations(self) -> List[VariationModel]:
        return self._variations

    def get_status(self) -> str:
        return self._status

    def get_type(self) -> str:
        return self._type

    def get_key(self) -> str:
        return self._key

    def get_is_always_check_segment(self) -> bool:
        return self._is_always_check_segment

    def get_name(self) -> str:
        return self._name

    def get_percent_traffic(self) -> Optional[int]:
        return self._percent_traffic

    def get_is_user_list_enabled(self) -> bool:
        return self.is_user_list_enabled

    def get_metrics(self) -> List[MetricModel]:
        return self._metrics

    def get_variables(self) -> List[VariableModel]:
        return self._variables

    def get_variation_id(self) -> int:
        return self._variation_id

    def get_campaign_id(self) -> int:
        return self._campaign_id

    def get_rule_key(self) -> str:
        return self._rule_key

    def set_rule_key(self, rule_key: str) -> None:
        self._rule_key = rule_key

    def set_variations(self, variations: List[VariationModel]) -> None:
        self._variations = variations

    def set_weight(self, weight: float) -> None:
        self._weight = weight

    def get_weight(self) -> float:
        return self._weight

    def get_start_range_variation(self) -> float:
        return self._start_range_variation

    def get_end_range_variation(self) -> float:
        return self._end_range_variation

    def set_start_range_variation(self, start_range_variation: float) -> None:
        self._start_range_variation = start_range_variation

    def set_end_range_variation(self, end_range_variation: float) -> None:
        self._end_range_variation = end_range_variation

    def get_salt(self) -> str:
        return self._salt