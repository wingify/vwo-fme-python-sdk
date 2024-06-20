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

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Now you can import the module
from vwo.packages.decision_maker.decision_maker import DecisionMaker


class DecisionMakerTest(unittest.TestCase):

    def setUp(self):
        self.decisionMaker = DecisionMaker()

    def test_generate_bucket_value(self):
        hash_value = 2147483647
        max_value = 100
        multiplier = 1
        expected_bucket_value = int(
            (max_value * (hash_value / (2**32)) + 1) * multiplier
        )
        bucket_value = self.decisionMaker.generate_bucket_value(
            hash_value, max_value, multiplier
        )
        self.assertEqual(bucket_value, expected_bucket_value)

    @patch.object(DecisionMaker, "generate_hash_value")
    def test_get_bucket_value_for_user(self, mock_generateHashValue):
        user_id = "user123"
        max_value = 100
        mock_hash_value = 123456789
        mock_generateHashValue.return_value = mock_hash_value

        expected_bucket_value = self.decisionMaker.generate_bucket_value(
            mock_hash_value, max_value
        )
        bucket_value = self.decisionMaker.get_bucket_value_for_user(user_id, max_value)

        self.assertEqual(bucket_value, expected_bucket_value)

    @patch.object(DecisionMaker, "generate_hash_value")
    def test_calculate_bucket_value(self, mock_generateHashValue):
        string = "testString"
        multiplier = 1
        max_value = 10000
        mock_hash_value = 987654321
        mock_generateHashValue.return_value = mock_hash_value

        expected_bucket_value = self.decisionMaker.generate_bucket_value(
            mock_hash_value, max_value, multiplier
        )
        bucket_value = self.decisionMaker.calculate_bucket_value(
            string, multiplier, max_value
        )

        self.assertEqual(bucket_value, expected_bucket_value)

    def test_generateHashValue(self):
        hash_key = "key123"
        expected_hash_value = 2360047679
        hash_value = self.decisionMaker.generate_hash_value(hash_key)
        self.assertEqual(hash_value, expected_hash_value)


if __name__ == "__main__":
    unittest.main()
