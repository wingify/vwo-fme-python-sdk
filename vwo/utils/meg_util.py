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


from typing import Any, Dict, List, Tuple, Optional
from ..enums.campaign_type_enum import CampaignTypeEnum
from ..models.settings.settings_model import SettingsModel
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.feature_model import FeatureModel
from ..models.campaign.variation_model import VariationModel
from ..models.user.context_model import ContextModel
from ..packages.logger.core.log_manager import LogManager
from ..services.campaign_decision_service import CampaignDecisionService
from ..utils.log_message_util import info_messages
from ..utils.campaign_util import (
    get_bucketing_seed,
    get_campaign_ids_from_feature_key,
    get_campaigns_by_group_id,
    get_feature_keys_from_campaign_ids,
    set_campaign_allocation,
    get_variation_from_campaign_key,
)
from ..utils.function_util import (
    clone_object,
    get_feature_from_key,
    get_specific_rules_based_on_type,
)
from ..packages.decision_maker.decision_maker import DecisionMaker
from ..utils.rule_evaluation_util import evaluate_rule
from ..utils.decision_util import evaluate_traffic_and_get_variation
from ..constants.Constants import Constants
from ..utils.model_utils import convert_campaign_to_variation_model
from ..services.storage_service import StorageService
from ..decorators.storage_decorator import StorageDecorator


def evaluate_groups(
    settings: SettingsModel,
    feature: FeatureModel,
    group_id: int,
    evaluated_feature_map: Dict[str, Any],
    context: ContextModel,
    storage_service: StorageService,
) -> Optional[VariationModel]:
    feature_to_skip = []
    campaign_map: Dict[str, List[CampaignModel]] = {}

    # Get all feature keys and all campaign IDs from the group ID
    result = get_feature_keys_from_group(settings, group_id)
    feature_keys = result["featureKeys"]
    group_campaign_ids = result["groupCampaignIds"]

    for feature_key in feature_keys:
        featureToEvaluate = get_feature_from_key(settings, feature_key)

        # Skip if the feature is already evaluated
        if feature_key in feature_to_skip:
            continue

        # Evaluate the feature rollout rules
        is_rollout_rule_passed = _is_rollout_rule_for_feature_passed(
            settings,
            featureToEvaluate,
            evaluated_feature_map,
            feature_to_skip,
            storage_service,
            context,
        )

        if is_rollout_rule_passed:
            for temp_feature in settings.get_features():
                if temp_feature.get_key() == feature_key:
                    for rule in temp_feature.get_rules_linked_campaign():
                        if (
                            str(rule.get_id()) in group_campaign_ids
                            or f"{rule.get_id()}_{rule.get_variations()[0].get_id()}"
                            in group_campaign_ids
                        ):
                            if feature_key not in campaign_map:
                                campaign_map[feature_key] = []
                            if not any(
                                item.get_rule_key() == rule.get_rule_key()
                                for item in campaign_map[feature_key]
                            ):
                                campaign_map[feature_key].append(rule)

    eligible_campaigns, eligible_campaigns_with_storage = _get_eligible_campaigns(
        settings, campaign_map, context, storage_service
    )

    return _find_winner_campaign_among_eligible_campaigns(
        settings,
        feature.get_key(),
        eligible_campaigns,
        eligible_campaigns_with_storage,
        group_id,
        context,
        storage_service,
    )


# Helper Functions


def get_feature_keys_from_group(
    settings: SettingsModel, group_id: int
) -> Dict[str, Any]:
    group_campaign_ids = get_campaigns_by_group_id(settings, group_id)
    feature_keys = get_feature_keys_from_campaign_ids(settings, group_campaign_ids)

    return {"featureKeys": feature_keys, "groupCampaignIds": group_campaign_ids}


def _is_rollout_rule_for_feature_passed(
    settings: SettingsModel,
    feature: FeatureModel,
    evaluated_feature_map: Dict[str, Any],
    feature_to_skip: List[str],
    storage_service: StorageService,
    context: ContextModel,
) -> bool:
    if (
        feature.get_key() in evaluated_feature_map
        and "rolloutId" in evaluated_feature_map[feature.get_key()]
    ):
        return True

    roll_out_rules = get_specific_rules_based_on_type(
        feature, CampaignTypeEnum.ROLLOUT.value
    )
    if roll_out_rules:
        for rule in roll_out_rules:
            pre_segmentation_result, whitelisted_object, updated_decision = (
                evaluate_rule(
                    settings,
                    feature,
                    rule,
                    context,
                    evaluated_feature_map,
                    {},
                    storage_service,
                    {},
                )
            )
            if pre_segmentation_result:
                variation = evaluate_traffic_and_get_variation(
                    settings, rule, context.get_id()
                )
                if isinstance(variation, VariationModel) and not None:
                    evaluated_feature_map[feature.get_key()] = {
                        "rolloutId": rule.get_id(),
                        "rolloutKey": rule.get_key(),
                        "rolloutVariationId": rule.get_variations()[0].get_id(),
                    }
                    return True

        # No rollout rule passed
        feature_to_skip.append(feature.get_key())
        return False

    # No rollout rule, evaluate experiments
    LogManager.get_instance().info(
        info_messages.get("MEG_SKIP_ROLLOUT_EVALUATE_EXPERIMENTS").format(
            featureKey=feature.get_key()
        )
    )
    return True


def _get_eligible_campaigns(
    settings: SettingsModel,
    campaign_map: Dict[str, List[CampaignModel]],
    context: ContextModel,
    storage_service: StorageService,
) -> Tuple[List[CampaignModel], List[CampaignModel]]:
    eligible_campaigns: List[CampaignModel] = []
    eligible_campaigns_with_storage: List[CampaignModel] = []

    for feature_key, campaigns in campaign_map.items():
        for campaign in campaigns:
            stored_data = StorageDecorator().get_feature_from_storage(
                feature_key, context, storage_service
            )

            if stored_data and stored_data.get("experimentVariationId"):
                if stored_data.get("experimentKey") == campaign.get_key():
                    variation = get_variation_from_campaign_key(
                        settings,
                        stored_data["experimentKey"],
                        stored_data["experimentVariationId"],
                    )
                    if variation:
                        LogManager.get_instance().info(
                            info_messages.get("MEG_CAMPAIGN_FOUND_IN_STORAGE").format(
                                campaignKey=(
                                    campaign.get_rule_key()
                                    if campaign.get_type() == CampaignTypeEnum.AB.value
                                    else campaign.get_name()
                                    + "_"
                                    + campaign.get_rule_key()
                                ),
                                userId=context.get_id(),
                            )
                        )
                        if not any(
                            item.get_key() == campaign.get_key()
                            for item in eligible_campaigns_with_storage
                        ):
                            eligible_campaigns_with_storage.append(
                                clone_object(campaign)
                            )
                        continue

            if CampaignDecisionService().get_pre_segmentation_decision(
                campaign, context
            ) and CampaignDecisionService().is_user_part_of_campaign(
                context.get_id(), campaign
            ):
                LogManager.get_instance().info(
                    info_messages.get("MEG_CAMPAIGN_ELIGIBLE").format(
                        campaignKey=campaign.get_rule_key(), userId=context.get_id()
                    )
                )
                eligible_campaigns.append(clone_object(campaign))
                continue

    return eligible_campaigns, eligible_campaigns_with_storage


def _find_winner_campaign_among_eligible_campaigns(
    settings: SettingsModel,
    feature_key: str,
    eligible_campaigns: List[CampaignModel],
    eligible_campaigns_with_storage: List[CampaignModel],
    group_id: int,
    context: ContextModel,
    storage_service: StorageService,
) -> Optional[VariationModel]:
    winner_campaign = None
    campaign_ids = get_campaign_ids_from_feature_key(settings, feature_key)
    meg_algo_number = (
        settings.get_groups().get(group_id, {}).get("et", Constants.RANDOM_ALGO)
    )

    if len(eligible_campaigns_with_storage) == 1:
        winner_campaign_found = eligible_campaigns_with_storage[0]
        LogManager.get_instance().info(
            info_messages.get("MEG_WINNER_CAMPAIGN").format(
                campaignKey=(
                    winner_campaign_found.get_key()
                    if winner_campaign_found.get_type() == CampaignTypeEnum.AB.value
                    else winner_campaign_found.get_name()
                    + "_"
                    + winner_campaign_found.get_rule_key()
                ),
                groupId=group_id,
                userId=context.get_id(),
                algo="",
            )
        )
        winner_campaign = convert_campaign_to_variation_model(winner_campaign_found)
    elif (
        len(eligible_campaigns_with_storage) > 1
        and meg_algo_number == Constants.RANDOM_ALGO
    ):
        winner_campaign = _normalize_weights_and_find_winning_campaign(
            eligible_campaigns_with_storage,
            context,
            campaign_ids,
            group_id,
            storage_service,
        )
    elif len(eligible_campaigns_with_storage) > 1:
        winner_campaign = _get_campaign_using_advanced_algo(
            settings,
            eligible_campaigns_with_storage,
            context,
            campaign_ids,
            group_id,
            storage_service,
        )

    if not eligible_campaigns_with_storage:
        if len(eligible_campaigns) == 1:
            winner_campaign_found = eligible_campaigns[0]
            LogManager.get_instance().info(
                info_messages.get("MEG_WINNER_CAMPAIGN").format(
                    campaignKey=(
                        winner_campaign_found.get_key()
                        if winner_campaign_found.get_type() == CampaignTypeEnum.AB.value
                        else winner_campaign_found.get_name()
                        + "_"
                        + winner_campaign_found.get_rule_key()
                    ),
                    groupId=group_id,
                    userId=context.get_id(),
                    algo="",
                )
            )
            winner_campaign = convert_campaign_to_variation_model(winner_campaign_found)
        elif len(eligible_campaigns) > 1 and meg_algo_number == Constants.RANDOM_ALGO:
            winner_campaign = _normalize_weights_and_find_winning_campaign(
                eligible_campaigns, context, campaign_ids, group_id, storage_service
            )
        elif len(eligible_campaigns) > 1:
            winner_campaign = _get_campaign_using_advanced_algo(
                settings,
                eligible_campaigns,
                context,
                campaign_ids,
                group_id,
                storage_service,
            )

    return winner_campaign


def _normalize_weights_and_find_winning_campaign(
    shortlisted_campaigns: List[CampaignModel],
    context: ContextModel,
    called_campaign_ids: List[int],
    group_id: int,
    storage_service: StorageService,
) -> Optional[VariationModel]:

    # Normalize weights and convert to VariationModel
    variation_models: List[VariationModel] = []
    for campaign in shortlisted_campaigns:
        # Example of weight normalization, to keep the result with four decimal places
        weight = round(100 / len(shortlisted_campaigns) * 10000) / 10000
        campaign.set_weight(weight)

        # Convert CampaignModel to VariationModel
        variation = convert_campaign_to_variation_model(campaign)

        # Append the created VariationModel to the new List
        variation_models.append(variation)

    set_campaign_allocation(variation_models)

    winner_campaign = CampaignDecisionService().get_variation(
        variation_models,
        DecisionMaker().calculate_bucket_value(
            get_bucketing_seed(context.get_id(), None, group_id)
        ),
    )

    if winner_campaign:
        LogManager.get_instance().info(
            info_messages.get("MEG_WINNER_CAMPAIGN").format(
                campaignKey=(
                    winner_campaign.get_key()
                    if winner_campaign.get_type() == CampaignTypeEnum.AB.value
                    else winner_campaign.get_name()
                    + "_"
                    + winner_campaign.get_rule_key()
                ),
                groupId=group_id,
                userId=context.get_id(),
                algo="using random algorithm",
            )
        )

        StorageDecorator().set_data_in_storage(
            {
                "featureKey": Constants.VWO_META_MEG_KEY + str(group_id),
                "context": context,
                "experimentId": winner_campaign.get_id(),
                "experimentKey": winner_campaign.get_key(),
                "experimentVariationId": (
                    winner_campaign.get_variations()[0].get_id()
                    if winner_campaign.get_type() == CampaignTypeEnum.PERSONALIZE.value
                    else -1
                ),
            },
            storage_service,
        )

        if winner_campaign.get_id() in called_campaign_ids:
            return winner_campaign
    else:
        LogManager.get_instance().info(
            f"No winner campaign found for group_id: {group_id} and user_id: {context.get_id()}"
        )
    return None


def _get_campaign_using_advanced_algo(
    settings: SettingsModel,
    shortlisted_campaigns: List[CampaignModel],
    context: ContextModel,
    called_campaign_ids: List[int],
    group_id: int,
    storage_service: StorageService,
) -> Optional[VariationModel]:
    winner_campaign = None
    found = False

    priority_order = settings.get_groups().get(group_id, {}).get("p", [])
    wt = settings.get_groups().get(group_id, {}).get("wt", {})

    for priority_id in priority_order:
        for campaign in shortlisted_campaigns:
            if str(campaign.get_id()) == priority_id:
                winner_campaign = convert_campaign_to_variation_model(campaign)
                found = True
                break
            elif (
                str(campaign.get_id())
                + "_"
                + str(campaign.get_variations()[0].get_id())
                == priority_id
            ):
                winner_campaign = convert_campaign_to_variation_model(campaign)
                found = True
                break
        if found:
            break

    if winner_campaign is None:
        participating_campaign_list: List[VariationModel] = []
        for campaign in shortlisted_campaigns:
            if str(campaign.get_id()) in wt:
                cloned_campaign = convert_campaign_to_variation_model(campaign)
                cloned_campaign.set_weight(wt[str(campaign.get_id())])
                participating_campaign_list.append(cloned_campaign)
            elif (
                str(campaign.get_id())
                + "_"
                + str(campaign.get_variations()[0].get_id())
                in wt
            ):
                cloned_campaign = convert_campaign_to_variation_model(campaign)
                cloned_campaign.set_weight(
                    wt[
                        str(campaign.get_id())
                        + "_"
                        + str(campaign.get_variations()[0].get_id())
                    ]
                )
                participating_campaign_list.append(cloned_campaign)

        set_campaign_allocation(participating_campaign_list)

        winner_campaign = CampaignDecisionService().get_variation(
            participating_campaign_list,
            DecisionMaker().calculate_bucket_value(
                get_bucketing_seed(context.get_id(), None, group_id)
            ),
        )

    if winner_campaign:
        LogManager.get_instance().info(
            info_messages.get("MEG_WINNER_CAMPAIGN").format(
                campaignKey=(
                    winner_campaign.get_key()
                    if winner_campaign.get_type() == CampaignTypeEnum.AB.value
                    else winner_campaign.get_name()
                    + "_"
                    + winner_campaign.get_rule_key()
                ),
                groupId=group_id,
                userId=context.get_id(),
                algo="using advanced algorithm",
            )
        )

        StorageDecorator().set_data_in_storage(
            {
                "featureKey": Constants.VWO_META_MEG_KEY + str(group_id),
                "context": context,
                "experimentId": winner_campaign.get_id(),
                "experimentKey": winner_campaign.get_key(),
                "experimentVariationId": (
                    winner_campaign.get_variations()[0].get_id()
                    if winner_campaign.get_type() == CampaignTypeEnum.PERSONALIZE.value
                    else -1
                ),
            },
            storage_service,
        )

        if winner_campaign.get_id() in called_campaign_ids:
            return winner_campaign
    else:
        LogManager.get_instance().info(
            f"No winner campaign found for group_id: {group_id} and user_id: {context.get_id()}"
        )
    return None
