# Copyright 2024-2026 Wingify Software Pvt. Ltd.
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
from ..services.hooks_manager import HooksManager
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
from ..utils.impression_util import (
    send_impression_for_variation_shown_batch,
    send_impression_for_variation_shown,
    create_and_send_impression_for_usage_tracking,
)
from ..models.user.get_flag import GetFlag
from ..services.storage_service import StorageService
from ..decorators.storage_decorator import StorageDecorator
from ..utils.campaign_util import get_variation_from_campaign_key
from ..enums.debug_category_enum import DebugCategoryEnum
from ..packages.logger.enums.log_level_enum import LogLevelEnum
from ..constants.Constants import Constants
from ..utils.debugger_service_util import send_debug_event_to_vwo
from ..utils.network_util import get_track_user_payload_data
from ..enums.event_enum import EventEnum
from ..services.settings_manager import SettingsManager
from ..utils.function_util import (
    get_current_unix_timestamp,
)
from ..utils.holdout_util import get_matched_holdouts, get_applicable_holdouts, send_network_calls_for_not_in_holdouts


class GetFlagApi:
    def __init__(self):
        self._should_check_for_experiment_rules = False
        self._passed_rules_information: Dict[str, Any] = {}
        self._evaluated_feature_map: Dict[str, Any] = {}

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

        # Flag for usage tracking - false if no variation shown call is sent
        is_variation_shown_fired = False

        feature = get_feature_from_key(settings, feature_key)
        is_enabled = False
        variables = []
        notInHoldoutIds: List[Any] = [];
        # Holdout-related keys as constants
        IS_IN_HOLDOUT_ID_KEY = "isInHoldoutId"
        HOLDOUT_GROUP_ID_KEY = "holdoutGroupId"
        NOT_IN_HOLDOUT_ID_KEY = "notInHoldoutId"
        MATCHED_HOLDOUTS_KEY = "matchedHoldouts"
        NOT_MATCHED_HOLDOUTS_KEY = "notMatchedHoldouts"
        HOLDOUT_PAYLOADS_KEY = "holdoutPayloads"

        decision = {
            "featureName": feature.get_name() if feature else None,
            "featureId": feature.get_id() if feature else None,
            "featureKey": feature.get_key() if feature else None,
            "userId": context.get_id() if context else None,
            "api": ApiEnum.GET_FLAG.value,
            "holdoutIDs": [],
            "isPartOfHoldout": False,
            "isHoldoutPresent": False,
            "isUserPartOfCampaign": False,
        }

        debug_event_props = {
            "an": ApiEnum.GET_FLAG.value,
            "fk": feature_key,
            "uuid": context.get_vwo_uuid(),
            "sId": context.get_session_id(),
        }

        storage_service = StorageService()
        stored_data = StorageDecorator().get_feature_from_storage(
            feature_key, context, storage_service
        )
        batchPayload = []


        # Check for holdout group persistence in storage and settings
        stored_is_in_holdout_id: List[Any] = (
            stored_data.get(IS_IN_HOLDOUT_ID_KEY)
            or stored_data.get(HOLDOUT_GROUP_ID_KEY)
            or []
        ) if stored_data else []
        stored_not_in_holdout_id: List[Any] = (
            stored_data.get(NOT_IN_HOLDOUT_ID_KEY) or []
        ) if stored_data else []
        if len(stored_is_in_holdout_id) > 0 or len(stored_not_in_holdout_id) > 0:
            # get all applicable holdouts for the feature from the latest settings
            applicable_holdouts = get_applicable_holdouts(settings, feature.get_id())

            if len(applicable_holdouts) > 0:
                for holdout in applicable_holdouts:
                    holdout_id = holdout.get_id()
                    # Check if stored_is_in_holdout_id contains the holdout_id
                    if holdout_id in stored_is_in_holdout_id:
                        LogManager.get_instance().info(
                            info_messages.get("STORED_HOLDOUT_DECISION_FOUND").format(
                                featureKey=feature_key,
                                userId=context.get_id(),
                                holdoutId=holdout_id,
                            )
                        )
                        # Evaluate the new holdouts in the settings file and prepare impressions
                        holdout_result = get_matched_holdouts(settings, feature, context, stored_data)
                        
                        matched_holdouts = holdout_result.get(MATCHED_HOLDOUTS_KEY, [])
                        not_matched_holdouts = holdout_result.get(NOT_MATCHED_HOLDOUTS_KEY, [])
                        holdout_payloads = holdout_result.get(HOLDOUT_PAYLOADS_KEY, [])
                        # updatedHoldoutIds = storedIsInHoldoutId + [id for matched_holdouts]
                        updated_holdout_ids = (
                            stored_is_in_holdout_id
                        ) + [h.get_id() for h in matched_holdouts]
                        updated_not_in_holdout_ids = (
                            stored_not_in_holdout_id
                        ) + [h.get_id() for h in not_matched_holdouts]

                        # Store the updated holdout ids in storage
                        StorageDecorator().set_data_in_storage(
                            {
                                "featureKey": feature_key,
                                "context": context,
                                IS_IN_HOLDOUT_ID_KEY: updated_holdout_ids,
                                NOT_IN_HOLDOUT_ID_KEY: updated_not_in_holdout_ids,
                            },
                            storage_service
                        )

                        # Send impression for the new holdouts
                        if SettingsManager.get_instance().is_gateway_service_provided:
                            for payload in holdout_payloads:
                                send_impression_for_variation_shown(
                                    payload,
                                    context
                                )
                        else:
                            send_impression_for_variation_shown_batch(holdout_payloads, account_id=settings.get_account_id(), sdk_key=settings.get_sdk_key())
                        
                        # if impression is fired for any of the holdouts, set is_variation_shown_fired to True
                        if holdout_payloads and len(holdout_payloads) > 0:
                            is_variation_shown_fired = True

                        # Case: User is already part of a holdout (stored decision).
                        if settings.get_is_tracking_usage_enabled() and not is_variation_shown_fired:
                            create_and_send_impression_for_usage_tracking(settings, feature_key, context)

                        # Return a disabled flag as user is in persistent holdout
                        return GetFlag(is_enabled=False, variables=[], session_id=context.get_session_id(), uuid=context.get_vwo_uuid())
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
                    decision["isUserPartOfCampaign"] = True
                    # send network calls for holdouts that are newly added in settings and are not present in storage
                    # Calculate the initial size of not_in_holdout_id
                    initial_size = len(stored_data.get("notInHoldoutId") or []) if stored_data else 0
                    # send network calls for not_in_holdout_id
                    updated_not_in_holdouts = send_network_calls_for_not_in_holdouts(settings, feature, context, decision, stored_data, storage_service)
                    # if variationShown event is fired, set is_variation_shown_fired to True - Optimization for newly added holdouts
                    if updated_not_in_holdouts and len(updated_not_in_holdouts) > initial_size:
                        is_variation_shown_fired = True

                    # Case: Feature found in storage
                    # Send usage tracking for cached experiment decision if usage tracking is enabled
                    if settings.get_is_tracking_usage_enabled() and not is_variation_shown_fired:
                        create_and_send_impression_for_usage_tracking(settings, feature_key, context)

                    return GetFlag(is_enabled=True, variables=variation.get_variables(), session_id=context.get_session_id(), uuid=context.get_vwo_uuid())
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

                decision["isUserPartOfCampaign"] = True
                # network calls for holdouts that are newly added in settings and are not present in storage
                # and return the updated not in holdout ids
                initial_size = len(stored_data.get("notInHoldoutId") or []) if stored_data else 0
                updated_not_in_holdout_ids = send_network_calls_for_not_in_holdouts(settings, feature, context, decision, stored_data, storage_service)
                if updated_not_in_holdout_ids and len(updated_not_in_holdout_ids) > initial_size:
                    is_variation_shown_fired = True
                # push the updated not in holdout ids to the notInHoldoutIds array
                notInHoldoutIds.extend(updated_not_in_holdout_ids)

                is_enabled = True
                variables = variation.get_variables()

                self._should_check_for_experiment_rules = True
                feature_info = {
                    "rolloutId": stored_data["rolloutId"],
                    "rolloutKey": stored_data["rolloutKey"],
                    "rolloutVariationId": stored_data["rolloutVariationId"],
                }
                self._evaluated_feature_map[feature_key] = feature_info
                self._passed_rules_information.update(feature_info)

        if feature is None:
            LogManager.get_instance().error_log("FEATURE_NOT_FOUND", data={"featureKey": feature_key}, debug_data = debug_event_props)
            is_enabled = False

            # Case: Feature not found
            # If usage tracking is enabled, send usage tracking impression
            if settings.get_is_tracking_usage_enabled() and not is_variation_shown_fired:
                create_and_send_impression_for_usage_tracking(settings, feature_key, context)

            return GetFlag(is_enabled=is_enabled, variables=variables, session_id=context.get_session_id(), uuid=context.get_vwo_uuid())
        
        if context.get_session_id() is None:
            context.set_session_id(get_current_unix_timestamp())

        SegmentationManager.get_instance().set_contextual_data(
            settings, feature, context
        )

        if not is_enabled:
            result = get_matched_holdouts(settings, feature, context, stored_data) or {}
            matched_holdouts = result.get(MATCHED_HOLDOUTS_KEY, [])
            not_matched_holdouts = result.get(NOT_MATCHED_HOLDOUTS_KEY, [])
            holdout_payloads = result.get(HOLDOUT_PAYLOADS_KEY, [])

            decision["isPartOfHoldout"] = matched_holdouts is not None and len(matched_holdouts) > 0

            if (
                (matched_holdouts is not None and len(matched_holdouts) > 0)
                or (not_matched_holdouts is not None and len(not_matched_holdouts) > 0)
            ):
                decision["isHoldoutPresent"] = True

            if matched_holdouts is not None and len(matched_holdouts) > 0:
                qualified_holdout_names = ",".join([holdout.get_name() for holdout in matched_holdouts])
                decision["holdoutIDs"] = [holdout.get_id() for holdout in matched_holdouts]

                LogManager.get_instance().info(
                    info_messages.get("USER_IN_HOLDOUT_GROUP").format(
                        userId=context.get_id(),
                        holdoutGroupName=qualified_holdout_names,
                        featureKey=feature_key,
                    )
                )

                StorageDecorator().set_data_in_storage(
                    {
                        "featureKey": feature_key,
                        "context": context,
                        IS_IN_HOLDOUT_ID_KEY: [holdout.get_id() for holdout in matched_holdouts],
                        NOT_IN_HOLDOUT_ID_KEY: [holdout.get_id() for holdout in not_matched_holdouts],
                    },
                    storage_service,
                )

                decision["isEnabled"] = False

                hook_manager.set(decision)
                hook_manager.execute(hook_manager.get())

                if SettingsManager.get_instance().is_gateway_service_provided:
                    for payload in holdout_payloads:
                        send_impression_for_variation_shown(payload, context)
                else:
                    send_impression_for_variation_shown_batch(
                        holdout_payloads, settings.get_account_id(), settings.get_sdk_key()
                    )

                return GetFlag(
                    is_enabled=False,
                    variables=[],
                    session_id=context.get_session_id(),
                    uuid=context.get_vwo_uuid(),
                )
            else:
                LogManager.get_instance().info(
                    info_messages.get("USER_NOT_EXCLUDED_DUE_TO_HOLDOUT").format(
                        featureKey=feature_key,
                        userId=context.get_id(),
                    )
                )
                notInHoldoutIds.extend([holdout.get_id() for holdout in not_matched_holdouts])

                if SettingsManager.get_instance().is_gateway_service_provided:
                    for payload in holdout_payloads:
                        send_impression_for_variation_shown(payload, context)
                else:
                    batchPayload.extend(holdout_payloads)

                if holdout_payloads and len(holdout_payloads) > 0:
                    is_variation_shown_fired = True

        roll_out_rules = get_specific_rules_based_on_type(
            feature, CampaignTypeEnum.ROLLOUT.value
        )

        if roll_out_rules and not is_enabled:
            rollout_rules_to_evaluate: List[CampaignModel] = []

            for rule in roll_out_rules:
                (
                    pre_segmentation_result,
                    whitelisted_object,
                    updated_decision,
                    payload,
                ) = evaluate_rule(
                    settings,
                    feature,
                    rule,
                    context,
                    self._evaluated_feature_map,
                    {},
                    storage_service,
                    decision,
                )
                decision.update(updated_decision)

                if pre_segmentation_result:
                    rollout_rules_to_evaluate.append(rule)

                    if (
                        SettingsManager.get_instance().is_gateway_service_provided
                        and payload is not None
                        and len(payload) > 0
                    ):
                        send_impression_for_variation_shown(payload, context)
                    else:
                        if payload is not None and len(payload) > 0:
                            batchPayload.append(payload)

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
                    settings, rollout_rules_to_evaluate[0], context
                )

                if isinstance(variation, VariationModel) and not None:
                    is_enabled = True
                    decision["isUserPartOfCampaign"] = True
                    variables = variation.get_variables()
                    self._should_check_for_experiment_rules = True
                    self._update_integrations_decision_object(
                        rollout_rules_to_evaluate[0], variation, decision
                    )

                    payload = get_track_user_payload_data(
                        settings,
                        EventEnum.VARIATION_SHOWN.value,
                        rollout_rules_to_evaluate[0].get_id(),
                        variation.get_id(),
                        context,
                    )
                    if (
                        SettingsManager.get_instance().is_gateway_service_provided
                        and payload is not None
                        and len(payload) > 0
                    ):
                        # set is_variation_shown_fired to true as the rollout impression is sent
                        is_variation_shown_fired = True
                        send_impression_for_variation_shown(payload, context)
                    else:
                        if payload is not None and len(payload) > 0:
                            # set is_variation_shown_fired to true as the rollout impression is sent
                            is_variation_shown_fired = True
                            batchPayload.append(payload)

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
                (
                    pre_segmentation_result,
                    whitelisted_object,
                    updated_decision,
                    payload,
                ) = evaluate_rule(
                    settings,
                    feature,
                    rule,
                    context,
                    self._evaluated_feature_map,
                    meg_group_winner_campaigns,
                    storage_service,
                    decision,
                )

                decision.update(updated_decision)

                if pre_segmentation_result:
                    if whitelisted_object is None:
                        experiment_rules_to_evaluate.append(rule)
                    else:
                        if (
                            SettingsManager.get_instance().is_gateway_service_provided
                            and payload is not None
                            and len(payload) > 0
                        ):
                            # set is_variation_shown_fired to true as the experiment impression is sent (for whitelisted user)
                            # this prevents sending usage tracking impression for the experiment campaign when checked at the bottom
                            is_variation_shown_fired = True
                            send_impression_for_variation_shown(payload, context)
                        else:
                            if payload is not None and len(payload) > 0:
                                # set is_variation_shown_fired to true as the experiment impression is sent (for whitelisted user)
                                # this prevents sending usage tracking impression for the experiment campaign when checked at the bottom
                                is_variation_shown_fired = True
                                batchPayload.append(payload)
                        
                        is_enabled = True
                        decision["isUserPartOfCampaign"] = True
                        variables = whitelisted_object["variation"].get_variables()
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
                    settings, experiment_rules_to_evaluate[0], context
                )

                if isinstance(variation, VariationModel) and not None:
                    is_enabled = True
                    decision["isUserPartOfCampaign"] = True
                    variables = variation.get_variables()

                    self._update_integrations_decision_object(
                        experiment_rules_to_evaluate[0], variation, decision
                    )

                    payload = get_track_user_payload_data(
                        settings,
                        EventEnum.VARIATION_SHOWN.value,
                        experiment_rules_to_evaluate[0].get_id(),
                        variation.get_id(),
                        context,
                    )
                    if (
                        SettingsManager.get_instance().is_gateway_service_provided
                        and payload is not None
                        and len(payload) > 0
                    ):
                        # set is_variation_shown_fired to true as the experiment impression is sent.
                        is_variation_shown_fired = True
                        send_impression_for_variation_shown(payload, context)
                    else:
                        if payload is not None and len(payload) > 0:
                            # set is_variation_shown_fired to true as the experiment impression is sent.
                            is_variation_shown_fired = True
                            batchPayload.append(payload)

        if is_enabled:
            StorageDecorator().set_data_in_storage(
                {
                    "featureKey": feature_key,
                    "context": context,
                    **self._passed_rules_information,
                    NOT_IN_HOLDOUT_ID_KEY: notInHoldoutIds,
                },
                storage_service,
            )
        else:
            StorageDecorator().set_data_in_storage(
                {
                    "featureKey": feature_key,
                    "context": context,
                    NOT_IN_HOLDOUT_ID_KEY: notInHoldoutIds,
                },
                storage_service,
            )

        hook_manager.set(decision)
        hook_manager.execute(hook_manager.get())

        # send debug event, if debugger is enabled
        if feature.get_is_debugger_enabled():
            debug_event_props["cg"] = DebugCategoryEnum.DECISION.value
            debug_event_props["lt"] = LogLevelEnum.INFO.value
            debug_event_props["msg_t"] = Constants.FLAG_DECISION_GIVEN
            
            # update debug event props with decision keys
            self.update_debug_event_props_with_message(debug_event_props, decision)
            send_debug_event_to_vwo(debug_event_props);

        if (
            feature.get_impact_campaign()
            and feature.get_impact_campaign().get_campaign_id()
        ):
            LogManager.get_instance().info(
                info_messages.get("IMPACT_ANALYSIS").format(
                    userId=context.get_id(),
                    featureKey=feature_key,
                    status=(
                        "enabled" if is_enabled else "disabled"
                    ),
                )
            )

            payload = get_track_user_payload_data(
                settings,
                EventEnum.VARIATION_SHOWN.value,
                feature.get_impact_campaign().get_campaign_id(),
                (2 if is_enabled else 1),
                context
            )
            if (
                SettingsManager.get_instance().is_gateway_service_provided
                and payload is not None
                and len(payload) > 0
            ):
                # set is_variation_shown_fired to true as the impact analysis impression is sent.
                is_variation_shown_fired = True
                send_impression_for_variation_shown(payload, context)
            else:
                if payload is not None and len(payload) > 0:
                    # set is_variation_shown_fired to true as the impact analysis impression is sent.
                    is_variation_shown_fired = True
                    batchPayload.append(payload)

        if not SettingsManager.get_instance().is_gateway_service_provided:
            send_impression_for_variation_shown_batch(
                batchPayload, settings.get_account_id(), settings.get_sdk_key()
            )

        # Send usage tracking call when no primary variationShown event was dispatched.
        # If a primary event was fired, the server already has the usage tracking signal.
        if settings.get_is_tracking_usage_enabled() and not is_variation_shown_fired:
            create_and_send_impression_for_usage_tracking(settings, feature_key, context)

        return GetFlag(is_enabled=is_enabled, variables=variables, session_id=context.get_session_id(), uuid=context.get_vwo_uuid())

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

    def update_debug_event_props_with_message(
        self,
        debug_event_props: Dict[str, Any],
        decision: Dict[str, Any],
    ) -> None:
        """
        Updates the debug event props with the decision keys.

        :param debug_event_props: The debug event props to update.
        :param decision: The decision object to extract the keys from.
        """
        feature_key = decision.get("featureKey") or ""
        message = f"Flag decision given for feature:{feature_key}."

        rollout_key = decision.get("rolloutKey")
        rollout_variation_id = decision.get("rolloutVariationId")
        if rollout_key and rollout_variation_id:
            prefix = f"{feature_key}_"
            rollout_suffix = (
                rollout_key[len(prefix):]
                if isinstance(rollout_key, str) and isinstance(feature_key, str) and rollout_key.startswith(prefix)
                else rollout_key
            )
            message += f" Got rollout:{rollout_suffix} with variation:{rollout_variation_id}"

        experiment_key = decision.get("experimentKey")
        experiment_variation_id = decision.get("experimentVariationId")
        if experiment_key and experiment_variation_id:
            prefix = f"{feature_key}_"
            experiment_suffix = (
                experiment_key[len(prefix):]
                if isinstance(experiment_key, str) and isinstance(feature_key, str) and experiment_key.startswith(prefix)
                else experiment_key
            )
            message += f" and experiment:{experiment_suffix} with variation:{experiment_variation_id}"
        debug_event_props["msg"] = message