# Copyright 2024 Wingify Software Pvt. Ltd.
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

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from ....data.dummy_test_data_reader import segmentor_dummy_dsl as TESTS_DATA

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Now you can import the module
from vwo.packages.segmentation_evaluator.evaluators.segment_evaluator import (
    SegmentEvaluator,
)


# Test class for Segmentation using unittest
class TestSegmentation(unittest.TestCase):
    def setUp(self):
        self.segment_evaluator = SegmentEvaluator()

    def test_and_operator(self):
        test_data = TESTS_DATA["and_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_case_insensitive_equality_operand(self):
        test_data = TESTS_DATA["case_insensitive_equality_operand"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_complex_and_ors(self):
        test_data = TESTS_DATA["complex_and_ors"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_complex_dsl(self):
        for test_case in [
            "complex_dsl_1",
            "complex_dsl_2",
            "complex_dsl_3",
            "complex_dsl_4",
        ]:
            test_data = TESTS_DATA[test_case]
            for key in test_data:
                dsl = test_data[key]["dsl"]
                expectation = test_data[key]["expectation"]
                custom_variables = test_data[key].get("customVariables", {})

                pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                    dsl, custom_variables
                )
                self.assertEqual(pre_segmentation_result, expectation)

    def test_contains_operand(self):
        test_data = TESTS_DATA["contains_operand"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_ends_with_operand(self):
        test_data = TESTS_DATA["ends_with_operand"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_equality_operand(self):
        test_data = TESTS_DATA["equality_operand"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_new_cases_for_decimal_mismatch(self):
        test_data = TESTS_DATA["new_cases_for_decimal_mismatch"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_not_operator(self):
        test_data = TESTS_DATA["not_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_or_operator(self):
        test_data = TESTS_DATA["or_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_regex(self):
        test_data = TESTS_DATA["regex"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_simple_and_ors(self):
        test_data = TESTS_DATA["simple_and_ors"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_starts_with_operand(self):
        test_data = TESTS_DATA["starts_with_operand"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_special_characters(self):
        test_data = TESTS_DATA["special_characters"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_user_operand_evaluator(self):
        test_data = TESTS_DATA["user_operand_evaluator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_user_operand_evaluator_with_customVariables(self):
        test_data = TESTS_DATA["user_operand_evaluator_with_customVariables"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_customVariables_with_greater_than_operator(self):
        test_data = TESTS_DATA["greater_than_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_customVariables_with_less_than_operator(self):
        test_data = TESTS_DATA["less_than_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_customVariables_with_greater_than_equal_to_operator(self):
        test_data = TESTS_DATA["greater_than_equal_to_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)

    def test_customVariables_with_less_than_equal_to_operator(self):
        test_data = TESTS_DATA["less_than_equal_to_operator"]
        for key in test_data:
            dsl = test_data[key]["dsl"]
            expectation = test_data[key]["expectation"]
            custom_variables = test_data[key].get("customVariables", {})

            pre_segmentation_result = self.segment_evaluator.is_segmentation_valid(
                dsl, custom_variables
            )
            self.assertEqual(pre_segmentation_result, expectation)


# To run the tests if this file is executed directly
if __name__ == "__main__":
    unittest.main()
