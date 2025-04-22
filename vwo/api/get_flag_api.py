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


from typing import Dict, Any, List
from ..models.settings.settings_model import SettingsModel
from ..models.user.context_model import ContextModel
from ..models.user.context_model import ContextModel
from ..services.hooks_manager import HooksManager
from ..packages.logger.core.log_manager import LogManager
from ..enums.api_enum import ApiEnum
from ..enums.campaign_type_enum import CampaignTypeEnum
from ..utils.log_message_util import debug_messages, info_messages, error_messages
from ..packages.logger.core.log_manager import LogManager
from ..utils.function_util import (
    get_feature_from_key,
    get_specific_rules_based_on_type,
    get_all_experiment_rules,
)
from ..models.campaign.campaign_model import CampaignModel
from ..models.campaign.variation_model import VariationModel
from ..packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)
from ..utils.rule_evaluation_util import evaluate_rule
from ..utils.decision_util import evaluate_traffic_and_get_variation
from ..utils.impression_util import create_and_send_impression_for_variation_shown
from ..models.user.get_flag import GetFlag
from ..services.storage_service import StorageService
from ..decorators.storage_decorator import StorageDecorator
from ..utils.campaign_util import get_variation_from_campaign_key


class GetFlagApi:
    def __init__(self):
        self._should_check_for_experiment_rules = False
        self._passed_rules_information: Dict[str, Any] = {}
        self._evaluated_feature_map: Dict[str, Any] = {}
        self._get_flag_response = GetFlag()

    def get(
        self,
        feature_key: str,
        settings: SettingsModel,
        context: ContextModel,
        hook_manager: HooksManager,
    ) -> GetFlag:
        """
        Gets the flag values for the given feature key.

        :param feature_key: The key of the feature to get the flag for.
        :param settings: The settings file containing the account settings.
        :param context: The context of the user.
        :param hook_manager: The hook manager to execute hooks.
        """

        feature = get_feature_from_key(settings, feature_key)
        decision = {
            "featureName": feature.get_name() if feature else None,
            "featureId": feature.get_id() if feature else None,
            "featureKey": feature.get_key() if feature else None,
            "userId": context.get_id() if context else None,
            "api": ApiEnum.GET_FLAG.value,
        }

        storage_service = StorageService()
        stored_data = StorageDecorator().get_feature_from_storage(
            feature_key, context, storage_service
        )

        if stored_data and stored_data.get("experimentVariationId"):
            if "experimentKey" in stored_data:
                variation = get_variation_from_campaign_key(
                    settings,
                    stored_data["experimentKey"],
                    stored_data["experimentVariationId"],
                )

                if variation:
                    LogManager.get_instance().info(
                        info_messages.get("STORED_VARIATION_FOUND").format(
                            variationKey=variation.get_name(),
                            userId=context.get_id(),
                            experimentType="experiment",
                            experimentKey=stored_data["experimentKey"],
                        )
                    )
                    self._get_flag_response.set_is_enabled(True)
                    self._get_flag_response.set_variables(variation.get_variables())
                    return self._get_flag_response
        elif (
            stored_data
            and stored_data.get("rolloutKey")
            and stored_data.get("rolloutId")
        ):
            variation = get_variation_from_campaign_key(
                settings, stored_data["rolloutKey"], stored_data["rolloutVariationId"]
            )
            if variation:
                LogManager.get_instance().info(
                    info_messages.get("STORED_VARIATION_FOUND").format(
                        variationKey=variation.get_name(),
                        userId=context.get_id(),
                        experimentType="rollout",
                        experimentKey=stored_data["rolloutKey"],
                    )
                )
                self._get_flag_response.set_is_enabled(True)
                self._get_flag_response.set_variables(variation.get_variables())
                self._should_check_for_experiment_rules = True
                feature_info = {
                    "rolloutId": stored_data["rolloutId"],
                    "rolloutKey": stored_data["rolloutKey"],
                    "rolloutVariationId": stored_data["rolloutVariationId"],
                }
                self._evaluated_feature_map[feature_key] = feature_info
                self._passed_rules_information.update(feature_info)

        if feature is None:
            LogManager.get_instance().error(
                error_messages.get("FEATURE_NOT_FOUND").format(
                    featureKey=feature_key,
                )
            )
            self._get_flag_response.set_is_enabled(False)
            return self._get_flag_response

        SegmentationManager.get_instance().set_contextual_data(
            settings, feature, context
        )

        roll_out_rules = get_specific_rules_based_on_type(
            feature, CampaignTypeEnum.ROLLOUT.value
        )

        if roll_out_rules and not self._get_flag_response.is_enabled():
            rollout_rules_to_evaluate: List[CampaignModel] = []

            for rule in roll_out_rules:
                pre_segmentation_result, whitelisted_object, updated_decision = (
                    evaluate_rule(
                        settings,
                        feature,
                        rule,
                        context,
                        self._evaluated_feature_map,
                        {},
                        storage_service,
                        decision,
                    )
                )

                decision.update(updated_decision)

                if pre_segmentation_result:
                    rollout_rules_to_evaluate.append(rule)

                    self._evaluated_feature_map[feature_key] = {
                        "rolloutId": rule.get_id(),
                        "rolloutKey": rule.get_key(),
                        "rolloutVariationId": (
                            rule.get_variations()[0].get_id()
                            if rule.get_variations()
                            else None
                        ),
                    }
                    break

            if rollout_rules_to_evaluate.__len__() > 0:
                variation = evaluate_traffic_and_get_variation(
                    settings, rollout_rules_to_evaluate[0], context.get_id()
                )

                if isinstance(variation, VariationModel) and not None:
                    self._get_flag_response.set_is_enabled(True)
                    self._get_flag_response.set_variables(variation.get_variables())
                    self._should_check_for_experiment_rules = True
                    self._update_integrations_decision_object(
                        rollout_rules_to_evaluate[0], variation, decision
                    )
                    create_and_send_impression_for_variation_shown(
                        settings,
                        rollout_rules_to_evaluate[0].get_id(),
                        variation.get_id(),
                        context,
                    )

        if not roll_out_rules:
            LogManager.get_instance().debug(
                debug_messages.get("EXPERIMENTS_EVALUATION_WHEN_NO_ROLLOUT_PRESENT")
            )
            self._should_check_for_experiment_rules = True

        if self._should_check_for_experiment_rules:
            experiment_rules_to_evaluate: List[CampaignModel] = []

            experiment_rules = get_all_experiment_rules(feature)
            meg_group_winner_campaigns = {}

            for rule in experiment_rules:
                pre_segmentation_result, whitelisted_object, updated_decision = (
                    evaluate_rule(
                        settings,
                        feature,
                        rule,
                        context,
                        self._evaluated_feature_map,
                        meg_group_winner_campaigns,
                        storage_service,
                        decision,
                    )
                )

                decision.update(updated_decision)

                if pre_segmentation_result:
                    if whitelisted_object is None:
                        experiment_rules_to_evaluate.append(rule)
                    else:
                        self._get_flag_response.set_is_enabled(True)
                        self._get_flag_response.set_variables(
                            whitelisted_object["variation"].get_variables()
                        )

                        self._passed_rules_information.update(
                            {
                                "experimentId": rule.get_id(),
                                "experimentKey": rule.get_key(),
                                "experimentVariationId": whitelisted_object[
                                    "variationId"
                                ],
                            }
                        )

                    break

            if experiment_rules_to_evaluate.__len__() > 0:
                variation = evaluate_traffic_and_get_variation(
                    settings, experiment_rules_to_evaluate[0], context.get_id()
                )

                if isinstance(variation, VariationModel) and not None:
                    self._get_flag_response.set_is_enabled(True)
                    self._get_flag_response.set_variables(variation.get_variables())

                    self._update_integrations_decision_object(
                        experiment_rules_to_evaluate[0], variation, decision
                    )
                    create_and_send_impression_for_variation_shown(
                        settings,
                        experiment_rules_to_evaluate[0].get_id(),
                        variation.get_id(),
                        context,
                    )

        if self._get_flag_response.is_enabled():
            StorageDecorator().set_data_in_storage(
                {
                    "featureKey": feature_key,
                    "context": context,
                    **self._passed_rules_information,
                },
                storage_service,
            )

        hook_manager.set(decision)
        hook_manager.execute(hook_manager.get())

        if (
            feature.get_impact_campaign()
            and feature.get_impact_campaign().get_campaign_id()
        ):
            LogManager.get_instance().info(
                info_messages.get("IMPACT_ANALYSIS").format(
                    userId=context.get_id(),
                    featureKey=feature_key,
                    status=(
                        "enabled"
                        if self._get_flag_response.is_enabled()
                        else "disabled"
                    ),
                )
            )

            create_and_send_impression_for_variation_shown(
                settings,
                feature.get_impact_campaign().get_campaign_id(),
                (
                    2 if self._get_flag_response.is_enabled() else 1
                ),  # 2 is for Variation (flag enabled), 1 is for Control (flag disabled)
                context,
            )

        return self._get_flag_response

    def _update_integrations_decision_object(
        self,
        campaign: CampaignModel,
        variation: VariationModel,
        decision: Dict[str, Any],
    ) -> None:
        if campaign.get_type() == CampaignTypeEnum.ROLLOUT.value:
            self._passed_rules_information.update(
                {
                    "rolloutId": campaign.get_id(),
                    "rolloutKey": campaign.get_key(),
                    "rolloutVariationId": variation.get_id(),
                }
            )
        else:
            self._passed_rules_information.update(
                {
                    "experimentId": campaign.get_id(),
                    "experimentKey": campaign.get_key(),
                    "experimentVariationId": variation.get_id(),
                }
            )
        decision.update(self._passed_rules_information)
