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

from typing import Any, Dict, List, Optional, Tuple

from ..models.settings.settings_model import SettingsModel
from ..models.campaign.holdout_model import HoldoutModel
from ..models.campaign.feature_model import FeatureModel
from ..models.user.context_model import ContextModel
from ..packages.decision_maker.decision_maker import DecisionMaker
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import debug_messages, info_messages
from ..utils.network_util import create_holdout_payload
from ..enums.event_enum import EventEnum
from ..constants.Constants import Constants
from ..services.storage_service import StorageService
from ..decorators.storage_decorator import StorageDecorator
from ..utils.impression_util import (
    send_impression_for_variation_shown,
    send_impression_for_variation_shown_batch,
)
from ..services.settings_manager import SettingsManager
from ..packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)


def get_applicable_holdouts(settings: SettingsModel, feature_id: int) -> List[HoldoutModel]:
    """
    Gets the applicable holdouts for a given feature ID.

    Args:
        settings: The settings object.
        feature_id: The feature ID.

    Returns:
        The applicable holdouts.
    """
    # Fallback to empty list if holdouts are not present or accessor not yet implemented
    holdouts: List[HoldoutModel] = []
    get_holdouts = getattr(settings, "get_holdouts", None)
    if callable(get_holdouts):
        holdouts = get_holdouts() or []

    # Filter the holdouts to only include global holdouts and holdouts that have the given feature ID
    return [
        holdout
        for holdout in holdouts
        if holdout.get_is_global() or feature_id in holdout.get_feature_ids()
    ]


def get_matched_holdouts(
    settings: SettingsModel,
    feature: FeatureModel,
    context: ContextModel,
    stored_data: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Gets the matched holdout(s) for a given feature ID and context.
    Evaluates all applicable holdouts, creates batched impressions for all of them,
    and returns all matched holdouts (i.e. holdouts the user is part of).

    Args:
        settings: The settings object.
        feature: The feature object.
        context: The context object.
        stored_data: Previously stored holdout data.

    Returns:
        A dict with matchedHoldouts, notMatchedHoldouts and holdoutPayloads, or None.
    """
    stored_data = stored_data or {}

    # stored_data has isInHoldoutId and notInHoldoutId, we need to use these to check if the holdout is already evaluated
    is_in_holdout_ids: List[int] = stored_data.get("isInHoldoutId") or []
    not_in_holdout_ids: List[int] = stored_data.get("notInHoldoutId") or []
    already_evaluated_holdout_ids = set(is_in_holdout_ids + not_in_holdout_ids)

    feature_id = feature.get_id()
    applicable_holdouts = get_applicable_holdouts(settings, feature_id)

    not_matched_holdouts: List[HoldoutModel] = []

    if not applicable_holdouts:
        return {"matchedHoldouts": [], "notMatchedHoldouts": [], "holdoutPayloads": []}

    matched_holdouts: List[HoldoutModel] = []
    holdout_payloads: List[Dict[str, Any]] = []

    log_manager = LogManager.get_instance()
    segmentation_manager = SegmentationManager.get_instance()

    for holdout in applicable_holdouts:
        if holdout.get_id() in already_evaluated_holdout_ids:
            log_manager.debug(
                debug_messages.get("HOLDOUT_SKIP_EVALUATION").format(
                    holdoutId=holdout.get_id(),
                    reason=f"user {context.get_id()} was already evaluated for feature with id: {feature_id}; SKIP decision making altogether.",
                )
            )
            continue

        segments = holdout.get_segments()
        segment_pass = True

        if segments and len(segments.keys()) > 0:
            segment_pass = segmentation_manager.validate_segmentation(
                segments, context.get_custom_variables()
            )
        else:
            log_manager.info(
                info_messages.get("HOLDOUT_SEGMENTATION_SKIP").format(
                    holdoutId=holdout.get_id(), userId=context.get_id()
                )
            )

        variation_id: int
        is_in_holdout = False

        if not segment_pass:
            log_manager.info(
                debug_messages.get("HOLDOUT_SEGMENTATION_FAIL").format(
                    userId=context.get_id(), holdoutGroupName=holdout.get_name()
                )
            )
            variation_id = Constants.VARIATION_NOT_PART_OF_HOLDOUT
            not_matched_holdouts.append(holdout)
        else:
            hash_key = f"{settings.get_account_id()}_{holdout.get_id()}_{context.get_id()}"
            bucket = DecisionMaker().get_bucket_value_for_user(hash_key, 100)

            is_in_holdout = bucket != 0 and bucket <= holdout.get_percent_traffic()
            variation_id = (
                Constants.VARIATION_IS_PART_OF_HOLDOUT
                if is_in_holdout
                else Constants.VARIATION_NOT_PART_OF_HOLDOUT
            )

            if is_in_holdout:
                log_manager.info(
                    info_messages.get("HOLDOUT_SHOULD_EXCLUDE_USER").format(
                        userId=context.get_id(),
                        bucketValue=bucket,
                        holdoutGroupName=holdout.get_name(),
                        percentTraffic=holdout.get_percent_traffic(),
                        featureKey=feature.get_key(),
                    )
                )
                matched_holdouts.append(holdout)
            else:
                log_manager.debug(
                    debug_messages.get("HOLDOUT_SHOULD_NOT_EXCLUDE_USER").format(
                        userId=context.get_id(),
                        holdoutGroupName=holdout.get_name(),
                        featureKey=feature.get_key(),
                    )
                )
                not_matched_holdouts.append(holdout)

        payload = create_holdout_payload(
            settings=settings,
            event_name=EventEnum.VWO_VARIATION_SHOWN.value,
            holdout_id=holdout.get_id(),
            variation_id=variation_id,
            context=context,
            feature_id=feature_id,
        )
        holdout_payloads.append(payload)

    return {
        "matchedHoldouts": matched_holdouts,
        "notMatchedHoldouts": not_matched_holdouts,
        "holdoutPayloads": holdout_payloads,
    }


def send_network_calls_for_not_in_holdouts(
    settings: SettingsModel,
    feature: FeatureModel,
    context: ContextModel,
    decision: Dict[str, Any],
    stored_data: Optional[Dict[str, Any]],
    storage_service: StorageService,
) -> List[Any]:
    """
    Sends network calls for not-in holdouts that are applicable but not stored in storage.

    Args:
        settings: The settings object.
        feature: The feature model.
        context: The context model.
        decision: The decision object (mutated to indicate if holdouts are present).
        stored_data: The stored data.
        storage_service: The storage service.

    Returns:
        Updated list of not-in holdout IDs.
    """
    stored_data = stored_data or {}

    applicable_holdouts = get_applicable_holdouts(settings, feature.get_id())
    updated_not_in_holdout_ids: List[Any] = list(stored_data.get("notInHoldoutId") or [])
    is_in_holdout_ids: List[Any] = list(stored_data.get("isInHoldoutId") or [])
    batch_payload: List[Dict[str, Any]] = []
    initial_not_in_holdout_count = len(updated_not_in_holdout_ids)

    if applicable_holdouts:
        decision["isHoldoutPresent"] = True

    for holdout in applicable_holdouts:
        if holdout.get_id() not in updated_not_in_holdout_ids and holdout.get_id() not in is_in_holdout_ids:
            updated_not_in_holdout_ids.append(holdout.get_id())

            payload = create_holdout_payload(
                settings=settings,
                event_name=EventEnum.VWO_VARIATION_SHOWN.value,
                holdout_id=holdout.get_id(),
                variation_id=Constants.VARIATION_NOT_PART_OF_HOLDOUT,
                context=context,
                feature_id=feature.get_id(),
            )

            if (
                SettingsManager.get_instance().is_gateway_service_provided
                and payload is not None
            ):
                send_impression_for_variation_shown(payload, context)
            else:
                if payload is not None:
                    batch_payload.append(payload)

    if len(updated_not_in_holdout_ids) > initial_not_in_holdout_count:
        StorageDecorator().set_data_in_storage(
            {
                "featureKey": feature.get_key(),
                "context": context,
                "notInHoldoutId": updated_not_in_holdout_ids,
            },
            storage_service,
        )

    if batch_payload:
        if SettingsManager.get_instance().is_gateway_service_provided:
            for payload in batch_payload:
                send_impression_for_variation_shown(payload, context)
        else:
            send_impression_for_variation_shown_batch(
                batch_payload, settings.get_account_id(), settings.get_sdk_key()
            )

    return updated_not_in_holdout_ids

