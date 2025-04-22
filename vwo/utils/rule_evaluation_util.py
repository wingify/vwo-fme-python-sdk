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


from ..models.settings.settings_model import SettingsModel
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.feature_model import FeatureModel
from ..models.user.context_model import ContextModel
from ..utils.data_type_util import is_object
from ..utils.decision_util import check_whitelisting_and_pre_seg
from ..utils.impression_util import create_and_send_impression_for_variation_shown
from ..services.storage_service import StorageService
from typing import Dict


def evaluate_rule(
    settings: SettingsModel,
    feature: FeatureModel,
    campaign: CampaignModel,
    context: ContextModel,
    evaluated_feature_map: Dict,
    meg_group_winner_campaigns: Dict,
    storage_service: StorageService,
    decision: Dict,
) -> Dict:
    """
    Evaluates the rules for a given campaign and feature based on the provided context.
    This function checks for whitelisting and pre-segmentation conditions, and if applicable,
    sends an impression for the variation shown.

    :param settings: SettingsModel object containing the settings configuration for the evaluation.
    :param feature: FeatureModel object representing the feature being evaluated.
    :param campaign: CampaignModel object associated with the feature.
    :param context: ContextModel object representing the user context for evaluation.
    :param evaluated_feature_map: A dictionary of evaluated features.
    :param meg_group_winner_campaigns: A dictionary of MEG group winner campaigns.
    :param storage_service: StorageService object for persistence.
    :param decision: The decision object that will be updated based on the evaluation.
    :return: A dictionary containing the result of the pre-segmentation and the whitelisted object, if any.
    """
    # Perform whitelisting and pre-segmentation checks
    pre_segmentation_result, whitelisted_object = check_whitelisting_and_pre_seg(
        settings,
        feature,
        campaign,
        context,
        evaluated_feature_map,
        meg_group_winner_campaigns,
        storage_service,
        decision,
    )

    # If pre-segmentation is successful and a whitelisted object exists, proceed to send an impression
    if (
        pre_segmentation_result
        and is_object(whitelisted_object)
        and len(whitelisted_object) > 0
    ):
        # Update the decision object with campaign and variation details
        decision.update(
            {
                "experimentId": campaign.get_id(),
                "experimentKey": campaign.get_key(),
                "experimentVariationId": whitelisted_object["variationId"],
            }
        )

        # Send an impression for the variation shown
        create_and_send_impression_for_variation_shown(
            settings,
            campaign.get_id(),
            whitelisted_object["variation"].get_id(),
            context,
        )

    # Return the results of the evaluation
    return pre_segmentation_result, whitelisted_object, decision
