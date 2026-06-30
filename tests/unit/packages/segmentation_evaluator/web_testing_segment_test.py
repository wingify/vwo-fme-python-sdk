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

import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from wingify.models.user.context_model import ContextModel
from wingify.packages.segmentation_evaluator.evaluators.segment_evaluator import (
    SegmentEvaluator,
)
from wingify.packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)
from wingify.packages.segmentation_evaluator.utils.web_testing_segment_util import (
    evaluate_web_testing_campaign_variation,
    normalize_web_testing_campaigns_map,
    parse_web_testing_campaigns_from_context,
)
from wingify.services.settings_manager import SettingsManager


def _context_with_platform_vars(extra: dict):
    base = {"id": "user-1", **extra}
    with patch.object(SettingsManager, "get_instance") as m:
        m.return_value.get_account_id.return_value = "1"
        return ContextModel(base)


class TestWebTestingSegmentUtil(unittest.TestCase):
    def test_evaluate_variation_patterns(self):
        campaign_assignments_map = {"1": "1", "2": "2"}
        self.assertTrue(evaluate_web_testing_campaign_variation("1_1", campaign_assignments_map)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("1_1", campaign_assignments_map)[1])
        self.assertFalse(evaluate_web_testing_campaign_variation("1_2", campaign_assignments_map)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("99_1", campaign_assignments_map)[0])
        self.assertTrue(evaluate_web_testing_campaign_variation("1_!2", campaign_assignments_map)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("1_!1", campaign_assignments_map)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("99_!1", campaign_assignments_map)[0])
        self.assertTrue(evaluate_web_testing_campaign_variation("!99", campaign_assignments_map)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("!1", campaign_assignments_map)[0])

    def test_null_map_like_node(self):
        self.assertTrue(evaluate_web_testing_campaign_variation("!1", None)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("1_1", None)[0])

    def test_invalid_encoding(self):
        evaluation_result_pair = evaluate_web_testing_campaign_variation("bogus", {"1": "1"})
        self.assertFalse(evaluation_result_pair[0])
        self.assertTrue(evaluation_result_pair[1])

    def test_multi_digit_ids(self):
        campaign_assignments_map = {"122": "4"}
        self.assertTrue(evaluate_web_testing_campaign_variation("122_4", campaign_assignments_map)[0])
        self.assertTrue(evaluate_web_testing_campaign_variation("122_!1", campaign_assignments_map)[0])
        self.assertFalse(evaluate_web_testing_campaign_variation("!122", campaign_assignments_map)[0])

    def test_campaign_only_any_variation(self):
        self.assertTrue(
            evaluate_web_testing_campaign_variation("100", {"100": "1"})[0]
        )
        self.assertTrue(
            evaluate_web_testing_campaign_variation("100", {"100": "9"})[0]
        )
        self.assertFalse(evaluate_web_testing_campaign_variation("100", {})[0])
        self.assertFalse(
            evaluate_web_testing_campaign_variation("100", {"99": "1"})[0]
        )
        self.assertFalse(
            evaluate_web_testing_campaign_variation(
                "100", {"1": "1", "2": "2"}
            )[0]
        )

    def test_normalize_coerces_types(self):
        self.assertEqual(
            normalize_web_testing_campaigns_map({129: 1, "14": 2}),
            {"129": "1", "14": "2"},
        )


class TestWebTestingSegmentEvaluator(unittest.TestCase):
    def _evaluator(self, context: ContextModel):
        ev = SegmentEvaluator()
        ev.context = context
        return ev

    def test_or_json_string_web_testing_campaigns(self):
        ctx = _context_with_platform_vars(
            {
                "platform_variables": {
                    "web_testing_campaigns": '{"1":"1"}',
                }
            }
        )
        ev = self._evaluator(ctx)
        self.assertTrue(ev.is_segmentation_valid({"or": [{"campaignVariation": "1_1"}]}, {}))

    def test_or_object_web_testing_campaigns(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": {"1": 1}}}
        )
        ev = self._evaluator(ctx)
        self.assertTrue(ev.is_segmentation_valid({"or": [{"campaignVariation": "1_1"}]}, {}))

    def test_not_in_campaign(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": "{}"}}
        )
        ev = self._evaluator(ctx)
        self.assertTrue(ev.is_segmentation_valid({"or": [{"campaignVariation": "!1"}]}, {}))

    def test_nested_not_campaign_variation(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": '{"1":"1"}'}}
        )
        ev = self._evaluator(ctx)
        self.assertFalse(
            ev.is_segmentation_valid({"not": {"campaignVariation": "1_1"}}, {})
        )

    def test_campaign_id_only(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": '{"100":"2"}'}}
        )
        ev = self._evaluator(ctx)
        self.assertTrue(ev.is_segmentation_valid({"or": [{"campaignVariation": "100"}]}, {}))

    def test_operand_trimmed(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": '{"1":"1"}'}}
        )
        ev = self._evaluator(ctx)
        self.assertTrue(
            ev.is_segmentation_valid({"or": [{"campaignVariation": "  1_1  "}]}, {})
        )

    def test_json_array_rejected(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": "[]"}}
        )
        ev = self._evaluator(ctx)
        self.assertFalse(
            ev.is_segmentation_valid({"or": [{"campaignVariation": "1_1"}]}, {})
        )

    def test_numeric_operand_coerced_to_string(self):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": '{"1":"1"}'}}
        )
        ev = self._evaluator(ctx)
        self.assertTrue(ev.is_segmentation_valid({"or": [{"campaignVariation": 1}]}, {}))
        ctx_float = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": '{"100":"2"}'}}
        )
        ev_float = self._evaluator(ctx_float)
        self.assertTrue(
            ev_float.is_segmentation_valid({"or": [{"campaignVariation": 100.0}]}, {})
        )


class TestWebTestingValidateSegmentationPrecheck(unittest.TestCase):
    def test_precheck_false_when_campaign_variation_without_assignments_feed(self):
        ctx = _context_with_platform_vars({})
        segmentation_manager = SegmentationManager.get_instance()
        segmentation_manager.attach_evaluator()
        segmentation_manager.evaluator.context = ctx
        self.assertFalse(
            segmentation_manager.validate_segmentation(
                {"not": {"campaignVariation": "1_1"}}, {}
            )
        )

    def test_precheck_true_when_campaign_variation_with_empty_assignment_object_string(
        self,
    ):
        ctx = _context_with_platform_vars(
            {"platform_variables": {"web_testing_campaigns": "{}"}}
        )
        segmentation_manager = SegmentationManager.get_instance()
        segmentation_manager.attach_evaluator()
        segmentation_manager.evaluator.context = ctx
        self.assertTrue(
            segmentation_manager.validate_segmentation(
                {"or": [{"campaignVariation": "!1"}]}, {}
            )
        )

    def test_duplicate_keys_in_json_string_last_value_wins(self):
        ctx = _context_with_platform_vars(
            {
                "platform_variables": {
                    "web_testing_campaigns": '{"122":"1","122":"2"}',
                }
            }
        )
        campaigns_map_from_context = parse_web_testing_campaigns_from_context(ctx)
        self.assertEqual(campaigns_map_from_context, {"122": "2"})


if __name__ == "__main__":
    unittest.main()