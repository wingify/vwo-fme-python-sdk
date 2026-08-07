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

"""Unit tests for campaign key helpers used in integrations callbacks and storage."""

import unittest

from wingify.enums.campaign_type_enum import CampaignTypeEnum
from wingify.models.campaign.campaign_model import CampaignModel
from wingify.models.campaign.variation_model import VariationModel
from wingify.models.settings.settings_model import SettingsModel
from wingify.utils.campaign_util import (
    get_experiment_key,
    get_rollout_key,
    get_variation_from_campaign_key,
)


def _make_campaign(
    campaign_type: str,
    key: str,
    rule_key: str,
    variations=None,
) -> CampaignModel:
    """
    Build a minimal ``CampaignModel`` for key-resolution tests.

    :param campaign_type: Campaign type value (e.g. ``FLAG_ROLLOUT``).
    :param key: Parent campaign key shared across linked rules.
    :param rule_key: Rule-specific key assigned after rule reordering.
    :param variations: Optional list of ``VariationModel`` instances.
    :return: A configured ``CampaignModel`` instance.
    """
    if variations is None:
        variations = []
    return CampaignModel(
        id=1,
        isForcedVariationEnabled=False,
        segments={},
        variations=variations,
        status="RUNNING",
        type=campaign_type,
        key=key,
        isAlwaysCheckSegment=False,
        name="campaign",
        rule_key=rule_key,
    )


def _make_variation(variation_id: int) -> VariationModel:
    """
    Build a minimal ``VariationModel`` for storage lookup tests.

    :param variation_id: Unique variation identifier.
    :return: A configured ``VariationModel`` instance.
    """
    return VariationModel(
        id=variation_id,
        segments={},
        weight=100,
        name="variation",
        variables=[],
        start_range_variation=0,
        end_range_variation=10000,
        key="variationKey",
        rule_key="ruleKey",
        type=CampaignTypeEnum.ROLLOUT.value,
    )


def _make_settings_with_linked_campaign(linked_campaign: CampaignModel) -> SettingsModel:
    """
    Build a ``SettingsModel`` with one feature and a linked campaign attached.

    :param linked_campaign: Linked rule campaign to attach to the feature.
    :return: Settings containing the feature with ``rules_linked_campaign`` set.
    """
    settings = SettingsModel(
        {
            "features": [
                {
                    "id": 1,
                    "key": "feature1",
                    "name": "Feature1",
                    "type": "FEATURE_FLAG",
                    "status": "ON",
                    "metrics": [],
                    "impactCampaign": {},
                    "rules": [],
                }
            ],
            "campaigns": [],
            "version": 1,
            "accountId": 12345,
            "sdkKey": "test-sdk-key",
        }
    )
    # Attach linked campaign directly — simulates post-init rule linking
    settings.get_features()[0].set_rules_linked_campaign([linked_campaign])
    return settings


class GetExperimentKeyTest(unittest.TestCase):
    """Tests for ``get_experiment_key()`` personalize rule key resolution."""

    def test_personalize_rule_uses_rule_key_when_parent_campaign_is_shared(self):
        """
        Verify personalize experiment key uses ``{featureKey}_{ruleKey}``.

        When multiple personalize rules share one parent campaign key, the resolved
        key must reflect the active rule (not always the first rule's key).

        :return: None. Asserts expected experiment key string.
        """
        # Parent key still points at first rule; rule_key identifies the active rule
        campaign = _make_campaign(
            CampaignTypeEnum.PERSONALIZE.value,
            "feature1_personalizeRule1",
            "personalizeRule2",
        )
        self.assertEqual(
            get_experiment_key(campaign, "feature1"), "feature1_personalizeRule2"
        )

    def test_personalize_rule_derives_feature_key_from_parent_campaign_key(self):
        """
        Verify feature key is derived from parent campaign key when omitted.

        :return: None. Asserts ``get_experiment_key`` resolves without explicit feature key.
        """
        campaign = _make_campaign(
            CampaignTypeEnum.PERSONALIZE.value,
            "feature1_personalizeRule1",
            "personalizeRule2",
        )
        # feature key inferred via parent key rsplit
        self.assertEqual(get_experiment_key(campaign), "feature1_personalizeRule2")

    def test_testing_rule_returns_campaign_key(self):
        """
        Verify AB/testing rules return the campaign key unchanged.

        Testing rules typically have unique campaign keys per rule, so no
        ``{featureKey}_{ruleKey}`` transformation is applied.

        :return: None. Asserts campaign key is returned as-is.
        """
        campaign = _make_campaign(
            CampaignTypeEnum.AB.value,
            "feature1_testingRule1",
            "testingRule1",
        )
        self.assertEqual(get_experiment_key(campaign, "feature1"), "feature1_testingRule1")


class GetRolloutKeyTest(unittest.TestCase):
    """Tests for ``get_rollout_key()`` rollout rule key resolution."""

    def test_rollout_rule_uses_rule_key_when_parent_campaign_is_shared(self):
        """
        Verify rollout key uses ``{featureKey}_{ruleKey}`` for shared parent campaigns.

        :return: None. Asserts resolved rollout key matches the active rule.
        """
        campaign = _make_campaign(
            CampaignTypeEnum.ROLLOUT.value,
            "feature1_rolloutRule1",
            "rolloutRule2",
        )
        self.assertEqual(get_rollout_key(campaign, "feature1"), "feature1_rolloutRule2")

    def test_rollout_rule_falls_back_to_campaign_key_for_first_rule(self):
        """
        Verify first rollout rule resolves to the same value as parent campaign key.

        When rule key matches the suffix of the parent key, result equals ``campaign.get_key()``.

        :return: None. Asserts backward-compatible key for the first rule.
        """
        campaign = _make_campaign(
            CampaignTypeEnum.ROLLOUT.value,
            "feature1_rolloutRule1",
            "rolloutRule1",
        )
        self.assertEqual(get_rollout_key(campaign, "feature1"), "feature1_rolloutRule1")


class GetVariationFromCampaignKeyTest(unittest.TestCase):
    """Tests for ``get_variation_from_campaign_key()`` linked-campaign lookup."""

    def test_finds_variation_for_linked_rollout_rule_key(self):
        """
        Verify storage lookup resolves rollout variations by resolved rule key.

        Lookup uses ``get_rollout_key`` against linked campaigns when the direct
        campaign key match fails.

        :return: None. Asserts the expected variation instance is returned.
        """
        variation = _make_variation(2)
        linked_campaign = _make_campaign(
            CampaignTypeEnum.ROLLOUT.value,
            "feature1_rolloutRule1",
            "rolloutRule2",
            variations=[variation],
        )
        settings = _make_settings_with_linked_campaign(linked_campaign)

        # Lookup by resolved key, not parent campaign key
        result = get_variation_from_campaign_key(
            settings, "feature1_rolloutRule2", 2
        )
        self.assertIs(result, variation)

    def test_finds_variation_for_linked_personalize_rule_key(self):
        """
        Verify storage lookup resolves personalize variations by resolved rule key.

        :return: None. Asserts the expected variation instance is returned.
        """
        variation = _make_variation(3)
        linked_campaign = _make_campaign(
            CampaignTypeEnum.PERSONALIZE.value,
            "feature1_personalizeRule1",
            "personalizeRule2",
            variations=[variation],
        )
        settings = _make_settings_with_linked_campaign(linked_campaign)

        result = get_variation_from_campaign_key(
            settings, "feature1_personalizeRule2", 3
        )
        self.assertIs(result, variation)


if __name__ == "__main__":
    unittest.main()
