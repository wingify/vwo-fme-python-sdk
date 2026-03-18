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
from ..enums.campaign_type_enum import CampaignTypeEnum
from ..models.campaign.variation_model import VariationModel
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import error_messages, debug_messages, info_messages
from ..constants.Constants import Constants
from ..packages.decision_maker.decision_maker import DecisionMaker
from ..models.user.context_model import ContextModel
from ..packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)
from ..utils.data_type_util import is_object
from ..models.vwo_options_model import VWOOptionsModel
from typing import List


class CampaignDecisionService:
    def __init__(self):
        self._decision_maker = DecisionMaker()

    def is_user_part_of_campaign(self, context: ContextModel, campaign: CampaignModel) -> bool:
        """
        Calculate if this user should become part of the campaign or not.

        :param context: the context model containing user ID and custom bucketing seed
        :param campaign: campaign model for getting the value of traffic allotted to the campaign
        :return: True if User is a part of Campaign, False otherwise
        """
        from ..utils.campaign_util import get_bucketing_id_for_user

        user_id = context.get_id()
        if not campaign or not user_id:
            return False

        bucketing_id = get_bucketing_id_for_user(context)

        is_rollout_or_personalize = campaign.get_type() in [    
            CampaignTypeEnum.ROLLOUT.value,
            CampaignTypeEnum.PERSONALIZE.value,
        ]

        # Get salt and traffic allocation based on campaign type
        if is_rollout_or_personalize:
            first_variation = campaign.get_variations()[0]
            salt = first_variation.get_salt()
            traffic_allocation = first_variation.get_weight()
        else:
            salt = campaign.get_salt()
            traffic_allocation = campaign.get_percent_traffic()

        # Generate bucket key using bucketing_id (custom seed or user_id)
        bucket_key = f"{salt}_{bucketing_id}" if salt else f"{campaign.get_id()}_{bucketing_id}"

        value_assigned_to_user = self._decision_maker.get_bucket_value_for_user(
            bucket_key
        )
        is_user_part = (
            value_assigned_to_user != 0 and value_assigned_to_user <= traffic_allocation
        )

        LogManager.get_instance().info(
            info_messages.get("USER_PART_OF_CAMPAIGN").format(
                userId=f"{user_id} (Seed: {bucketing_id})" if (bucketing_id != user_id) else user_id,
                notPart="" if is_user_part else "not",
                campaignKey=(
                    campaign.get_rule_key()
                    if campaign.get_type() == CampaignTypeEnum.AB.value
                    else campaign.get_name() + "_" + campaign.get_rule_key()
                ),
            )
        )

        return is_user_part

    def get_variation(
        self, variations: List[VariationModel], bucket_value: int
    ) -> VariationModel:
        """
        Returns the Variation by checking the Start and End Bucket Allocations of each Variation.

        :param variations: List of variations in the campaign
        :param bucket_value: the bucket Value of the user
        :return: VariationModel allotted to the user or None if not found
        """
        for variation in variations:
            if (
                variation.get_start_range_variation()
                <= bucket_value
                <= variation.get_end_range_variation()
            ):
                return variation

        return None

    def check_in_range(
        self, variation: VariationModel, bucket_value: int
    ) -> VariationModel:
        """
        Checks if the bucket value is in the range of the given variation.

        :param variation: Variation to check against
        :param bucket_value: The bucket value of the user
        :return: The variation if in range, None otherwise
        """
        if (
            variation.get_start_range_variation()
            <= bucket_value
            <= variation.get_end_range_variation()
        ):
            return variation
        return None

    def bucket_user_to_variation(
        self, context: ContextModel, account_id: str, campaign: CampaignModel
    ) -> VariationModel:
        """
        Validates the User ID and generates Variation into which the User is bucketed in.

        :param context: the context model containing user ID and custom bucketing seed
        :param account_id: the unique ID assigned to Account
        :param campaign: the Campaign of which User is a part of
        :return: VariationModel into which user is bucketed in or None if not
        """
        from ..utils.campaign_util import get_bucketing_id_for_user

        user_id = context.get_id()

        bucketing_id = get_bucketing_id_for_user(context)

        if not campaign or not bucketing_id:
            return None

        multiplier = 1 if campaign.get_percent_traffic() else None
        percent_traffic = campaign.get_percent_traffic()
        salt = campaign.get_salt()
        if salt:
            bucket_key = f"{salt}_{account_id}_{bucketing_id}"
        else:
            bucket_key = f"{campaign.get_id()}_{account_id}_{bucketing_id}"
        hash_value = self._decision_maker.generate_hash_value(bucket_key)
        bucket_value = self._decision_maker.generate_bucket_value(
            hash_value, Constants.MAX_TRAFFIC_VALUE, multiplier
        )

        LogManager.get_instance().debug(
            debug_messages.get("USER_BUCKET_TO_VARIATION").format(
                userId=f"{user_id} (Seed: {bucketing_id})" if (bucketing_id != user_id) else user_id,
                campaignKey=(
                    campaign.get_rule_key()
                    if campaign.get_type() == CampaignTypeEnum.AB.value
                    else campaign.get_name() + "_" + campaign.get_rule_key()
                ),
                percentTraffic=percent_traffic,
                bucketValue=bucket_value,
                hashValue=hash_value,
            )
        )

        return self.get_variation(campaign.get_variations(), bucket_value)

    def get_pre_segmentation_decision(
        self, campaign: CampaignModel, context: ContextModel
    ) -> bool:
        """
        Validates the pre-segmentation decision for the campaign and context.

        :param campaign: CampaignModel containing campaign data
        :param context: ContextModel containing user context data
        :return: True if segmentation is valid, False otherwise
        """
        campaign_type = campaign.get_type()
        segments = {}

        if campaign_type in [
            CampaignTypeEnum.ROLLOUT.value,
            CampaignTypeEnum.PERSONALIZE.value,
        ]:
            segments = campaign.get_variations()[0].get_segments()
        elif campaign_type == CampaignTypeEnum.AB.value:
            segments = campaign.get_segments()

        if is_object(segments) and not segments:
            LogManager.get_instance().info(
                info_messages.get("SEGMENTATION_SKIP").format(
                    userId=context.get_id(),
                    campaignKey=(
                        campaign.get_rule_key()
                        if campaign.get_type() == CampaignTypeEnum.AB.value
                        else campaign.get_name() + "_" + campaign.get_rule_key()
                    ),
                )
            )
            return True
        else:
            pre_segmentation_result = (
                SegmentationManager.get_instance().validate_segmentation(
                    segments, context.get_custom_variables()
                )
            )

            if not pre_segmentation_result:
                LogManager.get_instance().info(
                    info_messages.get("SEGMENTATION_STATUS").format(
                        userId=context.get_id(),
                        campaignKey=(
                            campaign.get_rule_key()
                            if campaign.get_type() == CampaignTypeEnum.AB.value
                            else campaign.get_name() + "_" + campaign.get_rule_key()
                        ),
                        status="failed",
                    )
                )
                return False

            LogManager.get_instance().info(
                info_messages.get("SEGMENTATION_STATUS").format(
                    userId=context.get_id(),
                    campaignKey=(
                        campaign.get_rule_key()
                        if campaign.get_type() == CampaignTypeEnum.AB.value
                        else campaign.get_name() + "_" + campaign.get_rule_key()
                    ),
                    status="passed",
                )
            )
            return True

    def get_variation_alloted(
        self, context: ContextModel, account_id: str, campaign: CampaignModel
    ) -> VariationModel:
        """
        Determines the variation allocated to the user for a given campaign.

        :param context: the context model containing user ID and custom bucketing seed
        :param account_id: the unique ID assigned to Account
        :param campaign: the Campaign of which User is a part of
        :return: The allocated VariationModel or None if not allocated
        """
        is_user_part = self.is_user_part_of_campaign(context, campaign)

        if campaign.get_type() in [
            CampaignTypeEnum.ROLLOUT.value,
            CampaignTypeEnum.PERSONALIZE.value,
        ]:
            if is_user_part:
                return campaign.get_variations()[0]
            else:
                return None
        else:
            if is_user_part:
                return self.bucket_user_to_variation(context, account_id, campaign)
            else:
                return None
