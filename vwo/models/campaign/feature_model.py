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


from typing import List, Dict, Any
from .metric_model import MetricModel
from .rule_model import RuleModel
from .rule_model import RuleModel
from .campaign_model import CampaignModel
from .impact_campaign_model import ImpactCampaignModel


class FeatureModel:
    def __init__(
        self,
        id: int,
        rules: List[RuleModel],
        status: str,
        key: str,
        metrics: List[MetricModel],
        impactCampaign: ImpactCampaignModel,
        type: str,
        name: str,
        rules_linked_campaign: List[CampaignModel] = [],
        is_gateway_service_required: bool = False,
    ):
        self._id = id
        self._rules = rules
        self._status = status
        self._key = key
        self._metrics = metrics
        self._impact_campaign = impactCampaign
        self._type = type
        self._name = name
        self._rules_linked_campaign = rules_linked_campaign
        self._is_gateway_service_required = is_gateway_service_required

    def get_id(self) -> int:
        return self._id

    def get_rules(self) -> List[RuleModel]:
        return self._rules

    def get_status(self) -> str:
        return self._status

    def get_key(self) -> str:
        return self._key

    def get_metrics(self) -> List[MetricModel]:
        return self._metrics

    def get_impact_campaign(self) -> ImpactCampaignModel:
        return self._impact_campaign

    def get_type(self) -> str:
        return self._type

    def get_name(self) -> str:
        return self._name

    def get_rules_linked_campaign(self) -> List[CampaignModel]:
        return self._rules_linked_campaign

    def get_is_gateway_service_required(self) -> bool:
        return self._is_gateway_service_required

    def set_rules_linked_campaign(
        self, rules_linked_campaign: List[CampaignModel]
    ) -> None:
        self._rules_linked_campaign = rules_linked_campaign

    def set_is_gateway_service_required(
        self, is_gateway_service_required: bool
    ) -> None:
        self._is_gateway_service_required = is_gateway_service_required
