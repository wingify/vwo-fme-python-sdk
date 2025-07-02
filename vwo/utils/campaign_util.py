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


from ..constants.Constants import Constants
from ..enums.campaign_type_enum import CampaignTypeEnum
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.feature_model import FeatureModel
from ..models.campaign.variation_model import VariationModel
from ..models.settings.settings_model import SettingsModel
from ..models.campaign.rule_model import RuleModel
from ..packages.logger.core.log_manager import LogManager
from .log_message_util import info_messages
from typing import Optional, Dict, List
import math


def set_variation_allocation(campaign: CampaignModel) -> None:
    """
    Allocates traffic ranges to variations within a campaign.

    If the campaign is of type ROLLOUT or PERSONALIZE, it handles the allocation specifically
    for rollout campaigns. Otherwise, it allocates the traffic range for each variation
    within the campaign by calling `assign_range_values`.

    Args:
        campaign (CampaignModel): The campaign object containing variations and their weights.

    Returns:
        None
    """
    if campaign.get_type() in [
        CampaignTypeEnum.ROLLOUT.value,
        CampaignTypeEnum.PERSONALIZE.value,
    ]:
        _handle_rollout_campaign(campaign)
    else:
        current_allocation = 0
        for variation in campaign.get_variations():
            step_factor = assign_range_values(variation, current_allocation)
            current_allocation += step_factor
            LogManager.get_instance().info(
                info_messages.get("VARIATION_RANGE_ALLOCATION").format(
                    variationKey=variation.get_name(),
                    campaignKey=campaign.get_rule_key(),
                    variationWeight=variation.get_weight(),
                    startRange=variation.get_start_range_variation(),
                    endRange=variation.get_end_range_variation(),
                )
            )


def assign_range_values(data: VariationModel, current_allocation: int) -> int:
    """
    Sets the start and end range values for a variation based on its weight.

    The function calculates the bucket range for the given variation weight and
    updates the start and end range for the variation.

    Args:
        data (VariationModel): The variation object containing the weight.
        current_allocation (int): The current allocation value from which the range starts.

    Returns:
        int: The step factor indicating the range size allocated to the variation.
    """
    step_factor = _get_variation_bucket_range(data.get_weight())

    if step_factor:
        data.set_start_range_variation(current_allocation + 1)
        data.set_end_range_variation(current_allocation + step_factor)
    else:
        data.set_start_range_variation(-1)
        data.set_end_range_variation(-1)

    return step_factor


def scale_variation_weights(variations: List[VariationModel]) -> None:
    """
    Scales the weights of variations to ensure they sum to 100.

    If the total weight of all variations is zero, each variation is assigned an equal weight.
    Otherwise, each variation's weight is scaled proportionally to ensure the total is 100.

    Args:
        variations (List[VariationModel]): List of variation objects to be scaled.

    Returns:
        None
    """
    total_weight = sum(variation.get_weight() for variation in variations)

    if total_weight == 0:
        equal_weight = 100 / len(variations)
        for variation in variations:
            variation.set_weight(equal_weight)
    else:
        for variation in variations:
            variation.set_weight((variation.get_weight() / total_weight) * 100)


def get_bucketing_seed(
    user_id: str, campaign: CampaignModel, group_id: Optional[int] = None
) -> str:
    """
    Generates a seed for bucketing based on user ID and campaign/group context.

    The seed is used for deterministic bucketing of users into variations or groups.
    If a group ID is provided, it combines the group ID and user ID. Otherwise,
    it combines the campaign ID and user ID.

    Args:
        user_id (str): The unique identifier for the user.
        campaign (CampaignModel): The campaign object for bucketing context.
        group_id (Optional[int]): The optional group ID if the campaign is part of a group.

    Returns:
        str: The generated bucketing seed.
    """
    if group_id is not None:
        return f"{group_id}_{user_id}"

    is_rollout_or_personalize = campaign.get_type() in [
        CampaignTypeEnum.ROLLOUT.value,
        CampaignTypeEnum.PERSONALIZE.value,
    ]
    if is_rollout_or_personalize:
        salt = campaign.get_variations()[0].get_salt()
    else:
        salt = campaign.get_salt()

    if salt:
        return f"{salt}_{user_id}"
    else:
        return f"{campaign.get_id()}_{user_id}"


def get_variation_from_campaign_key(
    settings: SettingsModel, campaign_key: str, variation_id: int
) -> Optional[VariationModel]:
    """
    Retrieves a variation from a campaign by its key and variation ID.

    Searches through all campaigns in the settings to find the specified campaign by its key,
    and then looks for the variation within that campaign by its ID.

    Args:
        settings (SettingsModel): The settings object containing campaign information.
        campaign_key (str): The key identifier for the campaign.
        variation_id (int): The unique identifier for the variation.

    Returns:
        Optional[VariationModel]: The variation object if found, otherwise None.
    """
    campaign = next(
        (c for c in settings.get_campaigns() if c.get_key() == campaign_key), None
    )

    if campaign:
        variation = next(
            (v for v in campaign.get_variations() if v.get_id() == variation_id), None
        )
        if variation:
            return variation

    return None


def set_campaign_allocation(campaigns: List[VariationModel]) -> None:
    """
    Sets the allocation ranges for a List of campaigns.

    Iterates through the provided campaigns and assigns range values for each campaign
    by calling `assign_range_values_meg`.

    Args:
        campaigns (List[VariationModel]): List of campaign objects to allocate.

    Returns:
        None
    """
    current_allocation = 0
    for campaign in campaigns:
        step_factor = assign_range_values_meg(campaign, current_allocation)
        current_allocation += step_factor


def get_group_details_if_campaign_part_of_it(
    settings: SettingsModel, campaign_id: str, variationId: Optional[int] = None
) -> Dict:
    """
    Retrieves group details if a campaign is part of a group.

    Looks up the group ID for the given campaign ID in the settings and returns
    the group details including the group ID and group name.

    Args:
        settings (SettingsModel): The settings object containing group information.
        campaign_id (int): The unique identifier for the campaign.
        variationId (Optional[int]): The unique identifier for the variation.

    Returns:
        Dict: A dictionary containing group ID and group name if the campaign is part of a group, otherwise an empty dictionary.
    """
    campaign_to_check = campaign_id
    if variationId:
        campaign_to_check = campaign_id + "_" + str(variationId)
    if (
        settings.get_campaign_groups()
        and campaign_to_check in settings.get_campaign_groups()
    ):
        group_id = str(settings.get_campaign_groups()[campaign_to_check])
        group_name = settings.get_groups()[group_id]["name"]
        return {"groupId": group_id, "groupName": group_name}

    return {}


def find_groups_feature_part_of(settings: SettingsModel, feature_key: str) -> List:
    """
    Finds all groups that a feature is part of.

    Searches through the features in the settings to find the feature by its key,
    then collects the group details for all campaigns associated with the feature.

    Args:
        settings (SettingsModel): The settings object containing feature information.
        feature_key (str): The key identifier for the feature.

    Returns:
        List: A List of dictionaries containing group details for each group the feature is part of.
    """
    ruleArrayList: List[RuleModel] = []

    for feature in settings.get_features():
        if feature.get_key() == feature_key:
            for rule in feature.get_rules():
                # Add rule to the array if it's not already present
                if rule not in ruleArrayList:
                    ruleArrayList.append(rule)

    groups = []

    # Iterate over each rule to find the group details
    for rule in ruleArrayList:
        group = get_group_details_if_campaign_part_of_it(
            settings,
            str(rule.get_campaign_id()),
            (
                rule.get_variation_id()
                if rule.get_type() == CampaignTypeEnum.PERSONALIZE.value
                else None
            ),
        )
        # Add group to the array if it's not already present
        if group.get("groupId") and group not in groups:
            groups.append(group)

    return groups


def get_campaigns_by_group_id(settings: SettingsModel, group_id: int) -> List:
    """
    Retrieves all campaigns associated with a given group ID.

    Looks up the group by its ID in the settings and returns the List of campaigns
    that are part of the group.

    Args:
        settings (SettingsModel): The settings object containing group information.
        group_id (int): The unique identifier for the group.

    Returns:
        List: A List of campaigns associated with the group.
    """
    group = settings.get_groups().get(group_id)
    if group:
        return group["campaigns"]
    return []


def get_feature_keys_from_campaign_ids(
    settings: SettingsModel, campaign_id_with_variation: List
) -> List:
    """
    Retrieves the feature keys associated with a List of campaign IDs.

    Iterates through the features in the settings and collects the keys of features
    that have rules linked to the provided campaign IDs.

    Args:
        settings (SettingsModel): The settings object containing feature information.
        campaign_ids (List): A List of campaign IDs to search for.

    Returns:
        List: A List of feature keys associated with the given campaign IDs.
    """
    feature_keys = []

    for campaign in campaign_id_with_variation:
        # split key with _ to separate campaignId and variationId
        campaign_id_variation_id = campaign.split("_")
        campaign_id = int(campaign_id_variation_id[0])
        variation_id = (
            int(campaign_id_variation_id[1])
            if len(campaign_id_variation_id) > 1
            else None
        )
        # Iterate over each feature to find the feature key
        for feature in settings.get_features():
            # check if feature is already present in the list
            if feature.get_key() in feature_keys:
                continue
            for rule in feature.get_rules():
                if rule.get_campaign_id() == campaign_id:
                    # Check if variationId is provided and matches the rule's variationId
                    if variation_id is not None:
                        # Add feature key if variationId matches
                        if rule.get_variation_id() == variation_id:
                            feature_keys.append(feature.get_key())
                    else:
                        # Add feature key if no variationId is provided
                        feature_keys.append(feature.get_key())

    return feature_keys


def get_campaign_ids_from_feature_key(
    settings: SettingsModel, feature_key: str
) -> List:
    """
    Retrieves the campaign IDs associated with a given feature key.

    Searches through the features in the settings to find the feature by its key,
    then collects the campaign IDs linked to that feature.

    Args:
        settings (SettingsModel): The settings object containing feature information.
        feature_key (str): The key identifier for the feature.

    Returns:
        List: A List of campaign IDs associated with the given feature key.
    """
    campaign_ids = []

    for feature in settings.get_features():
        if feature.get_key() == feature_key:
            for rule in feature.get_rules():
                campaign_ids.append(rule.get_campaign_id())

    return campaign_ids


def assign_range_values_meg(data: VariationModel, current_allocation: int) -> int:
    """
    Sets the start and end range values for a variation based on its weight (MEG version).

    The function calculates the bucket range for the given variation weight and
    updates the start and end range for the variation, starting from the current allocation.

    Args:
        data (VariationModel): The variation object containing the weight.
        current_allocation (int): The current allocation value from which the range starts.

    Returns:
        int: The step factor indicating the range size allocated to the variation.
    """
    step_factor = _get_variation_bucket_range(data.get_weight())

    if step_factor:
        data.set_start_range_variation(current_allocation)
        data.set_end_range_variation(current_allocation + step_factor)
    else:
        data.set_start_range_variation(-1)
        data.set_end_range_variation(-1)

    return step_factor


def get_rule_type_using_campaign_id_from_feature(
    feature: FeatureModel, campaign_id: int
) -> str:
    """
    Retrieves the rule type associated with a specific campaign ID from a feature.

    Searches through the rules of the feature to find the one linked to the given campaign ID,
    and returns the type of that rule.

    Args:
        feature (FeatureModel): The feature object containing rules.
        campaign_id (int): The unique identifier for the campaign.

    Returns:
        str: The type of the rule associated with the campaign ID, or an empty string if not found.
    """
    rule = next(
        (r for r in feature.get_rules() if r.get_campaign_id() == campaign_id), None
    )
    return rule.get_type() if rule else ""


def _get_variation_bucket_range(variation_weight: int) -> int:
    """
    Calculates the bucket range for a given variation weight.

    The function computes the range size based on the variation weight, ensuring
    it does not exceed the maximum traffic value.

    Args:
        variation_weight (int): The weight of the variation as an integer.

    Returns:
        int: The calculated range size for the variation weight.
    """
    if not variation_weight:
        return 0

    start_range = min(math.ceil(variation_weight * 100), Constants.MAX_TRAFFIC_VALUE)
    return start_range


def _handle_rollout_campaign(campaign: CampaignModel) -> None:
    """
    Handles the allocation of ranges for a rollout campaign.

    This function specifically deals with setting the range values for variations
    in a rollout campaign based on their weights.

    Args:
        campaign (CampaignModel): The rollout campaign object containing variations.

    Returns:
        None
    """
    for variation in campaign.get_variations():
        end_range = variation.get_weight() * 100
        variation.set_start_range_variation(1)
        variation.set_end_range_variation(end_range)

        LogManager.get_instance().info(
            info_messages.get("VARIATION_RANGE_ALLOCATION").format(
                variationKey=variation.get_name(),
                campaignKey=campaign.get_rule_key(),
                variationWeight=variation.get_weight(),
                startRange=1,
                endRange=end_range,
            )
        )