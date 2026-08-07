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

"""Unit tests for gateway gating in ``SegmentationManager.set_contextual_data``."""

import unittest
from unittest.mock import patch

from wingify.models.campaign.feature_model import FeatureModel
from wingify.models.campaign.impact_campaign_model import ImpactCampaignModel
from wingify.models.settings.settings_model import SettingsModel
from wingify.models.user.context_model import ContextModel
from wingify.packages.logger.core.log_manager import LogManager
from wingify.packages.network_layer.manager.network_manager import NetworkManager
from wingify.packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)
from wingify.services.settings_manager import SettingsManager


class SegmentationManagerGatewayTest(unittest.TestCase):
    """Tests that ``get-user-details`` is called only when gateway and segmentation require it."""

    def setUp(self):
        """
        Reset singletons and initialize logger/network for an isolated test run.

        :return: None.
        """
        SegmentationManager._instance = None
        SettingsManager._instance = None
        LogManager({"level": "ERROR"})
        NetworkManager.get_instance({})

    def _run_set_contextual_data(
        self,
        *,
        is_gateway_service_provided: bool,
        is_proxy_url_provided: bool,
        feature_requires_gateway: bool,
    ):
        """
        Execute ``set_contextual_data`` under a mocked gateway service call.

        :param is_gateway_service_provided: Whether ``gateway_service`` is passed to init.
        :param is_proxy_url_provided: Whether ``proxy_url`` is passed to init.
        :param feature_requires_gateway: Whether the feature flag marks gateway as required.
        :return: Mock object for ``get_from_gateway_service``.
        """
        init_options = {
            "sdk_key": "test-sdk-key",
            "account_id": "123456",
        }
        # Optional proxy — routes HTTP but does not enable gateway enrichment
        if is_proxy_url_provided:
            init_options["proxy_url"] = "http://localhost:3400"
        # Optional gateway — enables get-user-details when segmentation requires it
        if is_gateway_service_provided:
            init_options["gateway_service"] = {"url": "http://localhost:3000"}

        SettingsManager(init_options)

        feature = FeatureModel(
            id=1,
            key="feature1",
            name="Feature1",
            type="FEATURE_FLAG",
            status="ON",
            metrics=[],
            rules=[],
            impactCampaign=ImpactCampaignModel({}),
            is_gateway_service_required=feature_requires_gateway,
        )
        settings = SettingsModel(
            {
                "features": [],
                "campaigns": [],
                "version": 1,
                "accountId": 123456,
                "sdkKey": "test-sdk-key",
            }
        )
        # Context includes UA/IP fields used for gateway enrichment
        context = ContextModel(
            {
                "id": "user-1",
                "user_agent": "Mozilla/5.0 Test",
                "ip_address": "127.0.0.1",
            }
        )

        with patch(
            "wingify.packages.segmentation_evaluator.core.segmentation_manager.get_from_gateway_service"
        ) as mock_get_from_gateway:
            SegmentationManager.get_instance().set_contextual_data(
                settings, feature, context
            )
            return mock_get_from_gateway

    def test_proxy_url_only_with_ua_ip_does_not_call_gateway(self):
        """
        Verify proxy-only init does not call gateway when segmentation does not require it.

        ``proxy_url`` alone must not trigger ``get-user-details``.

        :return: None. Asserts gateway service is never invoked.
        """
        mock_get_from_gateway = self._run_set_contextual_data(
            is_gateway_service_provided=False,
            is_proxy_url_provided=True,
            feature_requires_gateway=False,
        )
        mock_get_from_gateway.assert_not_called()

    def test_gateway_service_without_segmentation_requirement_does_not_call(self):
        """
        Verify gateway configured without gateway-requiring segmentation skips the call.

        :return: None. Asserts gateway service is never invoked.
        """
        mock_get_from_gateway = self._run_set_contextual_data(
            is_gateway_service_provided=True,
            is_proxy_url_provided=False,
            feature_requires_gateway=False,
        )
        mock_get_from_gateway.assert_not_called()

    def test_gateway_service_with_segmentation_requirement_calls_gateway(self):
        """
        Verify gateway is called when both gateway is configured and segmentation needs it.

        :return: None. Asserts ``get_from_gateway_service`` is invoked exactly once.
        """
        mock_get_from_gateway = self._run_set_contextual_data(
            is_gateway_service_provided=True,
            is_proxy_url_provided=False,
            feature_requires_gateway=True,
        )
        mock_get_from_gateway.assert_called_once()

    def test_proxy_url_with_segmentation_requirement_does_not_call_gateway(self):
        """
        Verify proxy-only init does not call gateway even when segmentation requires it.

        Segmentation may fail quietly without gateway (no error log).

        :return: None. Asserts gateway service is never invoked.
        """
        mock_get_from_gateway = self._run_set_contextual_data(
            is_gateway_service_provided=False,
            is_proxy_url_provided=True,
            feature_requires_gateway=True,
        )
        mock_get_from_gateway.assert_not_called()

    def test_no_ua_or_ip_skips_gateway_even_when_required(self):
        """
        Verify gateway is not called when context lacks both user agent and IP address.

        Early return in ``set_contextual_data`` applies before gateway gating.

        :return: None. Asserts gateway service is never invoked.
        """
        SettingsManager(
            {
                "sdk_key": "test-sdk-key",
                "account_id": "123456",
                "gateway_service": {"url": "http://localhost:3000"},
            }
        )
        feature = FeatureModel(
            id=1,
            key="feature1",
            name="Feature1",
            type="FEATURE_FLAG",
            status="ON",
            metrics=[],
            rules=[],
            impactCampaign=ImpactCampaignModel({}),
            is_gateway_service_required=True,
        )
        settings = SettingsModel(
            {
                "features": [],
                "campaigns": [],
                "version": 1,
                "accountId": 123456,
                "sdkKey": "test-sdk-key",
            }
        )
        # No user_agent or ip_address — gateway enrichment cannot run
        context = ContextModel({"id": "user-1"})

        with patch(
            "wingify.packages.segmentation_evaluator.core.segmentation_manager.get_from_gateway_service"
        ) as mock_get_from_gateway:
            SegmentationManager.get_instance().set_contextual_data(
                settings, feature, context
            )
            mock_get_from_gateway.assert_not_called()


if __name__ == "__main__":
    unittest.main()
