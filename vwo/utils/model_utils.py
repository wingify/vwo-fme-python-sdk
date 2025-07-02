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


from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.rule_model import RuleModel
from ..models.campaign.metric_model import MetricModel
from ..models.campaign.feature_model import FeatureModel
from ..models.campaign.variable_model import VariableModel
from ..models.campaign.variation_model import VariationModel
from ..models.campaign.impact_campaign_model import ImpactCampaignModel
from typing import Dict, Any


def _parse_feature(feature_data: Dict[str, Any]) -> FeatureModel:
    rules = [_parse_rule(rule) for rule in feature_data["rules"]]
    metrics = [_parse_metric(metric) for metric in feature_data["metrics"]]
    return FeatureModel(
        id=feature_data["id"],
        rules=rules,
        status=feature_data.get("status", None),
        key=feature_data["key"],
        metrics=metrics,
        impactCampaign=ImpactCampaignModel(feature_data.get("impactCampaign", {})),
        type=feature_data["type"],
        name=feature_data["name"],
        rules_linked_campaign=[
            _parse_campaign(c) for c in feature_data.get("rulesLinkedCampaign", [])
        ],
        is_gateway_service_required=feature_data.get(
            "isgateway_serviceRequired", False
        ),
    )


def _parse_rule(rule_data: Dict[str, Any]) -> RuleModel:
    return RuleModel(
        type=rule_data["type"],
        ruleKey=rule_data.get("ruleKey"),
        variationId=rule_data.get("variationId", None),
        campaignId=rule_data["campaignId"],
    )


def _parse_metric(metric_data: Dict[str, Any]) -> MetricModel:
    return MetricModel(
        id=metric_data["id"],
        hasProps=metric_data.get("hasProps", None),
        type=metric_data["type"],
        identifier=metric_data["identifier"],
    )


def _parse_variable(variable_data: Dict[str, Any]) -> VariableModel:
    return VariableModel(
        id=variable_data["id"],
        value=variable_data["value"],
        type=variable_data["type"],
        key=variable_data["key"],
    )


def _parse_variation(variation_data: Dict[str, Any]) -> VariationModel:
    variables = [_parse_variable(var) for var in variation_data.get("variables", [])]
    return VariationModel(
        id=variation_data.get("id", None),
        segments=variation_data.get("segments", {}),
        weight=variation_data.get("weight", None),
        name=variation_data.get("name", None),
        variables=variables,
        start_range_variation=variation_data.get("startRangeVariation", None),
        end_range_variation=variation_data.get("endRangeVariation", None),
        key=variation_data.get("key", None),
        rule_key=variation_data.get("ruleKey", None),
        type=variation_data.get("type", None),
        variations=[
            _parse_variation(var) for var in variation_data.get("variations", [])
        ],
        salt=variation_data.get("salt", None),
    )


def _parse_campaign(campaign_data: Dict[str, Any]) -> CampaignModel:
    variations = [_parse_variation(var) for var in campaign_data.get("variations", [])]
    return CampaignModel(
        id=campaign_data["id"],
        isForcedVariationEnabled=campaign_data.get("isForcedVariationEnabled", False),
        segments=campaign_data.get("segments", {}),
        variations=variations,
        status=campaign_data["status"],
        type=campaign_data["type"],
        key=campaign_data["key"],
        isAlwaysCheckSegment=campaign_data.get("isAlwaysCheckSegment", False),
        name=campaign_data["name"],
        percentTraffic=campaign_data.get("percentTraffic", None),
        is_user_list_enabled=campaign_data.get("isUserListEnabled", False),
        metrics=campaign_data.get("metrics", []),
        variables=campaign_data.get("variables", []),
        variation_id=campaign_data.get("variationId", None),
        campaign_id=campaign_data.get("campaignId", None),
        rule_key=campaign_data.get("ruleKey", None),
        weight=campaign_data.get("weight", None),
        start_range_variation=campaign_data.get("startRangeVariation", None),
        end_range_variation=campaign_data.get("endRangeVariation", None),
        salt=campaign_data.get("salt", None),
    )


def convert_campaign_to_variation_model(campaign: CampaignModel):
    return VariationModel(
        campaign.get_id(),
        campaign.get_segments(),
        campaign.get_weight(),
        campaign.get_name(),
        campaign.get_variables(),
        campaign.get_start_range_variation(),
        campaign.get_end_range_variation(),
        campaign.get_key(),
        campaign.get_rule_key(),
        campaign.get_type(),
        campaign.get_variations(),
        campaign.get_salt(),
    )