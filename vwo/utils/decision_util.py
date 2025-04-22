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
from ..enums.status_enum import StatusEnum
from ..enums.campaign_type_enum import CampaignTypeEnum
from ..models.settings.settings_model import SettingsModel
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.feature_model import FeatureModel
from ..models.user.context_model import ContextModel
from ..packages.logger.core.log_manager import LogManager
from ..services.campaign_decision_service import CampaignDecisionService
from ..utils.log_message_util import info_messages
from ..utils.uuid_util import get_uuid
from ..utils.campaign_util import (
    get_group_details_if_campaign_part_of_it,
    scale_variation_weights,
    assign_range_values,
    get_bucketing_seed,
)
from ..utils.data_type_util import is_object
from ..utils.function_util import clone_object
from ..packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)
from ..packages.decision_maker.decision_maker import DecisionMaker
from ..services.storage_service import StorageService
from ..decorators.storage_decorator import StorageDecorator
from ..constants.Constants import Constants


def check_whitelisting_and_pre_seg(
    settings: SettingsModel,
    feature: FeatureModel,
    campaign: CampaignModel,
    context: ContextModel,
    evaluated_feature_map: Dict[str, Any],
    meg_group_winner_campaigns: Dict,
    storage_service: StorageService,
    decision: Any,
):
    """
    Check whitelisting and pre-segmentation.

    :param settings: SettingsModel object containing configuration.
    :param feature: FeatureModel object representing the feature.
    :param campaign: CampaignModel object representing the campaign.
    :param context: ContextModel object containing user context.
    :param evaluated_feature_map: Map of evaluated features.
    :param meg_group_winner_campaigns: Map of winner campaigns for mutually exclusive groups.
    :param storage_service: StorageService object for storage operations.
    :param decision: Dictionary to store decision details.
    :return: Tuple (boolean indicating success, any result data).
    """
    vwo_user_id = get_uuid(context.get_id(), settings.get_account_id())
    campaign_id = campaign.get_id()
    if campaign.get_type() == CampaignTypeEnum.AB.value:
        context.set_variation_targeting_variables(
            {
                **context.get_variation_targeting_variables(),
                "_vwoUserId": (
                    vwo_user_id
                    if campaign.get_is_user_list_enabled()
                    else context.get_id()
                ),
            }
        )
        decision["variation_targeting_variables"] = (
            context.get_variation_targeting_variables()
        )
        if campaign.get_is_forced_variation_enabled():
            whitelisted_variation = _check_campaign_whitelisting(campaign, context)
            if whitelisted_variation and whitelisted_variation:
                return True, whitelisted_variation
        else:
            LogManager.get_instance().info(
                info_messages.get("WHITELISTING_SKIP").format(
                    campaignKey=campaign.get_rule_key(),
                    userId=context.get_id(),
                    variation="",
                )
            )
    context.set_custom_variables(
        {
            **context.get_custom_variables(),
            "_vwoUserId": (
                vwo_user_id if campaign.get_is_user_list_enabled() else context.get_id()
            ),
        }
    )

    decision["custom_variables"] = context.get_custom_variables()
    group_details = get_group_details_if_campaign_part_of_it(
        settings,
        str(campaign_id),
        (
            campaign.get_variations()[0].get_id()
            if campaign.get_type() == CampaignTypeEnum.PERSONALIZE.value
            else None
        ),
    )
    group_id = group_details.get("groupId")
    group_winner_campaign_id = meg_group_winner_campaigns.get(group_id)

    if group_winner_campaign_id:
        if campaign.get_type() == CampaignTypeEnum.AB.value:
            # check if the campaign is the winner of the group
            if group_winner_campaign_id == campaign_id:
                return True, None
        elif campaign.get_type() == CampaignTypeEnum.PERSONALIZE.value:
            # check if the campaign is the winner of the group
            if group_winner_campaign_id == str(campaign_id) + "_" + str(
                campaign.get_variations()[0].get_id()
            ):
                return True, None
        # as group is already evaluated, no need to check again, return false directly
        return False, None
    elif group_id:
        # check in storage if the group is already evaluated for the user
        stored_data = StorageDecorator().get_feature_from_storage(
            Constants.VWO_META_MEG_KEY + group_id, context, storage_service
        )
        if (
            stored_data
            and stored_data.get("experimentKey")
            and stored_data.get("experimentId")
        ):
            LogManager.get_instance().info(
                info_messages.get("MEG_CAMPAIGN_FOUND_IN_STORAGE").format(
                    campaignKey=stored_data.get("experimentKey"),
                    userId=context.get_id(),
                )
            )
            if stored_data.get("experimentId") == campaign_id:
                # return the campaign if the called campaignId matches
                if campaign.get_type() == CampaignTypeEnum.PERSONALIZE.value:
                    if (
                        stored_data.get("experimentVariationId")
                        == campaign.get_variations()[0].get_id()
                    ):
                        # if personalise then check if the reqeusted variation is the winner
                        return True, None
                    else:
                        # if requested variation is not the winner then set the winner campaign in the map and return
                        meg_group_winner_campaigns[group_id] = (
                            str(stored_data.get("experimentId"))
                            + "_"
                            + str(campaign.get_variations()[0].get_id())
                        )
                        return False, None
                else:
                    return True, None
            if stored_data.get("experimentVariationId") != -1:
                meg_group_winner_campaigns[group_id] = (
                    str(stored_data.get("experimentId"))
                    + "_"
                    + str(stored_data.get("experimentVariationId"))
                )
            else:
                meg_group_winner_campaigns[group_id] = stored_data.get("experimentId")
            return False, None

    is_pre_segmentation_passed = (
        CampaignDecisionService().get_pre_segmentation_decision(campaign, context)
    )

    from ..utils.meg_util import evaluate_groups

    if is_pre_segmentation_passed and group_id:
        winner_campaign = evaluate_groups(
            settings, feature, group_id, evaluated_feature_map, context, storage_service
        )
        if winner_campaign and winner_campaign.get_id() == campaign_id:
            if winner_campaign.get_type() == CampaignTypeEnum.AB.value:
                return True, None
            else:
                # if personalise then check if the reqeusted variation is the winner
                if (
                    winner_campaign.get_variations()[0].get_id()
                    == campaign.get_variations()[0].get_id()
                ):
                    return True, None
                else:
                    meg_group_winner_campaigns[group_id] = (
                        str(winner_campaign.get_id())
                        + "_"
                        + str(winner_campaign.get_variations()[0].get_id())
                    )
                    return False, None
        elif winner_campaign:
            if winner_campaign.get_type() == CampaignTypeEnum.AB.value:
                meg_group_winner_campaigns[group_id] = winner_campaign.get_id()
            else:
                meg_group_winner_campaigns[group_id] = (
                    str(winner_campaign.get_id())
                    + "_"
                    + str(winner_campaign.get_variations()[0].get_id())
                )
            return False, None
        meg_group_winner_campaigns[group_id] = -1
        return False, None

    return is_pre_segmentation_passed, None


def evaluate_traffic_and_get_variation(
    settings: SettingsModel, campaign: CampaignModel, user_id: str
):
    """
    Evaluate the traffic and get the variation for the user.

    :param settings: SettingsModel object containing configuration.
    :param campaign: CampaignModel object representing the campaign.
    :param user_id: User ID.
    :return: VariationModel object if a variation is allocated, None otherwise.
    """
    variation = CampaignDecisionService().get_variation_alloted(
        user_id, settings.get_account_id(), campaign
    )

    if not variation:
        LogManager.get_instance().info(
            info_messages.get("USER_CAMPAIGN_BUCKET_INFO").format(
                campaignKey=(
                    campaign.get_rule_key()
                    if campaign.get_type() == CampaignTypeEnum.AB.value
                    else campaign.get_name() + "_" + campaign.get_rule_key()
                ),
                userId=user_id,
                status="did not get any variation",
            )
        )
        return None

    LogManager.get_instance().info(
        info_messages.get("USER_CAMPAIGN_BUCKET_INFO").format(
            campaignKey=(
                campaign.get_rule_key()
                if campaign.get_type() == CampaignTypeEnum.AB.value
                else campaign.get_name() + "_" + campaign.get_rule_key()
            ),
            userId=user_id,
            status=f"got variation: {variation.get_name()}",
        )
    )

    return variation


def _check_campaign_whitelisting(campaign: CampaignModel, context: ContextModel):
    """
    Check for whitelisting in the campaign.

    :param campaign: CampaignModel object.
    :param context: ContextModel object.
    :return: Whitelisting result.
    """
    whitelisting_result = _evaluate_whitelisting(campaign, context)
    status = StatusEnum.PASSED.value if whitelisting_result else StatusEnum.FAILED.value
    variation_string = (
        whitelisting_result["variation"].get_name() if whitelisting_result else ""
    )

    LogManager.get_instance().info(
        info_messages.get("WHITELISTING_STATUS").format(
            userId=context.get_id(),
            campaignKey=(
                campaign.get_rule_key()
                if campaign.get_type() == CampaignTypeEnum.AB.value
                else campaign.get_name() + "_" + campaign.get_rule_key()
            ),
            status=status,
            variationString=variation_string,
        )
    )

    return whitelisting_result


def _evaluate_whitelisting(campaign: CampaignModel, context: ContextModel):
    """
    Evaluate whitelisting for the campaign.

    :param campaign: CampaignModel object.
    :param context: ContextModel object.
    :return: Whitelisted variation result.
    """
    targeted_variations = []

    for variation in campaign.get_variations():
        if is_object(variation.get_segments()) and not variation.get_segments():
            LogManager.get_instance().info(
                info_messages.get("WHITELISTING_SKIP").format(
                    campaignKey=(
                        campaign.get_rule_key()
                        if campaign.get_type() == CampaignTypeEnum.AB.value
                        else campaign.get_name() + "_" + campaign.get_rule_key()
                    ),
                    userId=context.get_id(),
                    variation=(
                        f"for variation: {variation.get_name()}"
                        if variation.get_name()
                        else ""
                    ),
                )
            )
            continue

        if is_object(variation.get_segments()):
            segment_evaluator_result = (
                SegmentationManager.get_instance().validate_segmentation(
                    variation.get_segments(),
                    context.get_variation_targeting_variables(),
                )
            )

            if segment_evaluator_result:
                targeted_variations.append(clone_object(variation))

    if len(targeted_variations) > 1:
        scale_variation_weights(targeted_variations)
        current_allocation = 0
        for i, variation in enumerate(targeted_variations):
            step_factor = assign_range_values(variation, current_allocation)
            current_allocation += step_factor

        whitelisted_variation = CampaignDecisionService().get_variation(
            targeted_variations,
            DecisionMaker().calculate_bucket_value(
                get_bucketing_seed(context.get_id(), campaign, None)
            ),
        )
    else:
        whitelisted_variation = targeted_variations[0] if targeted_variations else None

    if whitelisted_variation:
        return {
            "variation": whitelisted_variation,
            "variationName": whitelisted_variation.get_name(),
            "variationId": whitelisted_variation.get_id(),
        }
    return None
