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


from ....enums.url_enum import UrlEnum
from ....models.user.context_vwo_model import ContextVWOModel
from ....packages.logger.core.log_manager import LogManager
from ....services.settings_manager import SettingsManager
from ...segmentation_evaluator.evaluators.segment_evaluator import SegmentEvaluator
from ....models.settings.settings_model import SettingsModel
from ....models.campaign.feature_model import FeatureModel
from ....models.user.context_model import ContextModel
from ....utils.gateway_service_util import get_query_params, get_from_gateway_service
from ....constants.Constants import Constants
from ....enums.api_enum import ApiEnum
from ..utils.web_testing_segment_util import (
    dsl_contains_campaign_variation_node,
    is_web_testing_campaigns_absent_or_null,
)


class SegmentationManager:
    _instance = None  # Singleton instance of SegmentationManager
    evaluator = None  # Holds the instance of SegmentEvaluator

    def __new__(cls):
        """
        Singleton pattern implementation for creating the instance of SegmentationManager.
        """
        if cls._instance is None:
            cls._instance = super(SegmentationManager, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def get_instance():
        """
        Singleton pattern implementation for getting the instance of SegmentationManager.

        :return: The singleton instance.
        """
        if SegmentationManager._instance is None:
            SegmentationManager._instance = SegmentationManager()
        return SegmentationManager._instance

    def attach_evaluator(self, evaluator=None):
        """
        Attaches an evaluator to the manager, or creates a new one if none is provided.

        :param evaluator: Optional evaluator to attach.
        """
        if evaluator:
            self.evaluator = evaluator
        else:
            self.evaluator = SegmentEvaluator()

    def set_contextual_data(
        self, settings: SettingsModel, feature: FeatureModel, context: ContextModel
    ):
        """
        Sets the contextual data for the segmentation process.

        :param settings: The settings data.
        :param feature: The feature data including segmentation needs.
        :param context: The context data for the evaluation.
        """
        self.attach_evaluator()  # Ensure a fresh evaluator instance
        self.evaluator.settings = settings  # Set settings in evaluator
        self.evaluator.context = context  # Set context in evaluator
        self.evaluator.feature = feature  # Set feature in evaluator

        # if both user agent and ip address is none or empty then return
        if not context.get_user_agent() and not context.get_ip_address():
            return

        # Check if any holdout requires gateway service
        holdouts = settings.get_holdouts() or []
        is_gateway_service_required_for_holdouts = len(
            list(
                filter(
                    lambda holdout: holdout.get_is_gateway_service_required(), holdouts
                )
            )
        ) > 0
        is_segmentation_gateway_required = (
            feature.get_is_gateway_service_required()
            or is_gateway_service_required_for_holdouts
        )
        # Call get-user-details only when gateway_service is configured and
        # segmentation (feature or holdout) requires gateway data.
        # proxy_url alone must never trigger a gateway call.
        should_call_gateway_service = (
            SettingsManager.get_instance().is_gateway_service_provided
            and is_segmentation_gateway_required
        )

        if should_call_gateway_service and context.get_vwo() is None:
            query_params = {}
            if not context.get_user_agent() and not context.get_ip_address():
                return
                
            if context.get_user_agent():
                query_params["userAgent"] = context.get_user_agent()

            if context.get_ip_address():
                query_params["ipAddress"] = context.get_ip_address()

            try:
                params = get_query_params(query_params)
                _vwo = get_from_gateway_service(params, UrlEnum.GET_USER_DATA.value, context)
                context.set_vwo(ContextVWOModel(_vwo))
            except Exception as err:
                LogManager.get_instance().error_log("ERROR_SETTING_SEGMENTATION_CONTEXT",data={"err": str(err)}, debug_data={"an": ApiEnum.GET_FLAG.value, "uuid": context.get_vwo_uuid(), "sId": context.get_session_id()})

    def validate_segmentation(self, dsl, properties):
        """
        Validates the segmentation against provided DSL and properties.

        :param dsl: The segmentation DSL.
        :param properties: The properties to validate against.
        :return: True if segmentation is valid, otherwise False.
        """
        # if the dsl contains a campaign variation node, then we need to check if the campaign variation is valid
        if dsl_contains_campaign_variation_node(dsl):
            evaluation_context = getattr(self.evaluator, "context", None)
            if evaluation_context is None or is_web_testing_campaigns_absent_or_null(
                evaluation_context
            ):
                return False
        return self.evaluator.is_segmentation_valid(dsl, properties)
