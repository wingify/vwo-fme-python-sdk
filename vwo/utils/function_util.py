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


import json
from typing import Any, List, Optional, Dict
import time
import random
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.feature_model import FeatureModel
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.feature_model import FeatureModel
from ..models.settings.settings_model import SettingsModel
from ..enums.campaign_type_enum import CampaignTypeEnum
import copy


def clone_object(obj: Any) -> Any:
    if obj is None:
        return obj
    return copy.deepcopy(obj)


def get_current_unix_timestamp() -> int:
    return int(time.time())


def get_current_unix_timestamp_in_millis() -> int:
    return int(time.time() * 1000)


def get_random_number() -> float:
    return random.random()


def get_specific_rules_based_on_type(
    feature: FeatureModel, type: Optional[str] = None
) -> List[CampaignModel]:
    if not feature or not feature.get_rules_linked_campaign():
        return []

    if type:
        return [
            rule
            for rule in feature.get_rules_linked_campaign()
            if rule.get_type() == type
        ]

    return feature.get_rules_linked_campaign()


def get_all_experiment_rules(feature: FeatureModel) -> List[CampaignModel]:
    if not feature:
        return []

    return [
        rule
        for rule in feature.get_rules_linked_campaign()
        if rule.get_type()
        in [CampaignTypeEnum.AB.value, CampaignTypeEnum.PERSONALIZE.value]
    ]


def get_feature_from_key(
    settings: SettingsModel, feature_key: str
) -> Optional[FeatureModel]:
    if not settings or not settings.get_features():
        return None

    for feature in settings.get_features():
        if feature.get_key() == feature_key:
            return feature

    return None


def does_event_belong_to_any_feature(event_name: str, settings: SettingsModel) -> bool:
    if not settings or not settings.get_features():
        return False

    return any(
        any(metric.get_identifier() == event_name for metric in feature.get_metrics())
        for feature in settings.get_features()
    )


def add_linked_campaigns_to_settings(settings: SettingsModel):
    """
    Add linked campaigns to the settings object.

    :param settings: The settings object containing campaigns and features.
    """
    # Create a dictionary for quick access to campaigns by ID
    campaign_map = {
        campaign.get_id(): campaign for campaign in settings.get_campaigns()
    }

    # Loop over all features
    for feature in settings.get_features():
        rules_linked_campaign_model = []

        for rule in feature.get_rules():
            original_campaign = campaign_map.get(rule.get_campaign_id())
            if original_campaign is None:
                continue

            # Copy original campaign to a new campaign object
            campaign = CampaignModel(
                id=original_campaign.get_id(),
                isForcedVariationEnabled=original_campaign.get_is_forced_variation_enabled(),
                segments=original_campaign.get_segments(),
                variations=original_campaign.get_variations(),
                status=original_campaign.get_status(),
                type=original_campaign.get_type(),
                key=original_campaign.get_key(),
                isAlwaysCheckSegment=original_campaign.get_is_always_check_segment(),
                name=original_campaign.get_name(),
                percentTraffic=original_campaign.get_percent_traffic(),
                is_user_list_enabled=original_campaign.get_is_user_list_enabled(),
                metrics=original_campaign.get_metrics(),
                variables=original_campaign.get_variables(),
                variation_id=original_campaign.get_variation_id(),
                campaign_id=original_campaign.get_campaign_id(),
                rule_key=original_campaign.get_rule_key(),
                salt=original_campaign.get_salt(),
            )

            # Set the rule key for the campaign
            campaign.set_rule_key(rule.get_rule_key())

            # If a variationId is specified, find and add the variation
            if rule.get_variation_id() is not None:
                variation = next(
                    (
                        v
                        for v in campaign.get_variations()
                        if v.get_id() == rule.get_variation_id()
                    ),
                    None,
                )
                if variation is not None:
                    campaign.set_variations([variation])

            rules_linked_campaign_model.append(campaign)

        # Assign the linked campaigns to the feature
        feature.set_rules_linked_campaign(rules_linked_campaign_model)