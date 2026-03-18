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

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from vwo import init

# Mock settings matching Node.js test for parity
MOCK_SETTINGS_FILE = {
    "version": 1,
    "sdkKey": "abcdef",
    "accountId": 123456,
    "campaigns": [
        {
            "segments": {},
            "status": "RUNNING",
            "variations": [
                {
                    "weight": 100,
                    "segments": {},
                    "id": 1,
                    "variables": [
                        {
                            "id": 1,
                            "type": "string",
                            "value": "def",
                            "key": "kaus"
                        }
                    ],
                    "name": "Rollout-rule-1"
                }
            ],
            "type": "FLAG_ROLLOUT",
            "isAlwaysCheckSegment": False,
            "isForcedVariationEnabled": False,
            "name": "featureOne : Rollout",
            "key": "featureOne_rolloutRule1",
            "id": 1
        },
        {
            "segments": {},
            "status": "RUNNING",
            "key": "featureOne_testingRule1",
            "type": "FLAG_TESTING",
            "isAlwaysCheckSegment": False,
            "name": "featureOne : Testing rule 1",
            "isForcedVariationEnabled": True,
            "variations": [
                {
                    "weight": 50,
                    "segments": {},
                    "id": 1,
                    "variables": [
                        {
                            "id": 1,
                            "type": "string",
                            "value": "def",
                            "key": "kaus"
                        }
                    ],
                    "name": "Default"
                },
                {
                    "weight": 50,
                    "segments": {},
                    "id": 2,
                    "variables": [
                        {
                            "id": 1,
                            "type": "string",
                            "value": "var1",
                            "key": "kaus"
                        }
                    ],
                    "name": "Variation-1"
                },
                {
                    "weight": 0,
                    "segments": {
                        "or": [
                            {
                                "user": "forcedKaustubh"
                            }
                        ]
                    },
                    "id": 3,
                    "variables": [
                        {
                            "id": 1,
                            "type": "string",
                            "value": "var2",
                            "key": "kaus"
                        }
                    ],
                    "name": "Variation-2"
                },
                {
                    "weight": 0,
                    "segments": {},
                    "id": 4,
                    "variables": [
                        {
                            "id": 1,
                            "type": "string",
                            "value": "var3",
                            "key": "kaus"
                        }
                    ],
                    "name": "Variation-3"
                }
            ],
            "id": 2,
            "percentTraffic": 100
        }
    ],
    "features": [
        {
            "impactCampaign": {},
            "rules": [
                {
                    "campaignId": 1,
                    "type": "FLAG_ROLLOUT",
                    "ruleKey": "rolloutRule1",
                    "variationId": 1
                },
                {
                    "type": "FLAG_TESTING",
                    "ruleKey": "testingRule1",
                    "campaignId": 2
                }
            ],
            "status": "ON",
            "key": "featureOne",
            "metrics": [
                {
                    "type": "CUSTOM_GOAL",
                    "identifier": "e1",
                    "id": 1
                }
            ],
            "type": "FEATURE_FLAG",
            "name": "featureOne",
            "id": 1
        }
    ]
}


class TestGetFlagWithoutBucketingSeed(unittest.TestCase):
    """Test cases for getFlag without bucketing seed."""

    sdk_key = "abcdef"
    account_id = "123456"

    def test_should_assign_different_variations_to_users_with_different_user_ids(self):
        """
        Case 1: Standard bucketing (no custom seed)
        Scenario: Two different users ('KaustubhVWO', 'RandomUserVWO') with NO bucketing seed.
        Expected: They should be bucketed into different variations based on their User IDs.
        We know from our settings that KaustubhVWO -> Variation-1 and RandomUserVWO -> Default.
        """
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            user1_flag = vwo_client.get_flag("featureOne", {"id": "KaustubhVWO"})
            user2_flag = vwo_client.get_flag("featureOne", {"id": "RandomUserVWO"})

            # Users with different IDs should get different variations for this split
            self.assertNotEqual(user1_flag.get_variables(), user2_flag.get_variables())


class TestGetFlagWithBucketingSeed(unittest.TestCase):
    """Test cases for getFlag with bucketing seed."""

    sdk_key = "abcdef"
    account_id = "123456"

    def test_should_assign_same_variation_to_different_users_with_same_bucketing_seed(self):
        """
        Case 2: Bucketing Seed Provided
        Scenario: Two different users ('KaustubhVWO', 'RandomUserVWO') are provided with the SAME bucketingSeed.
        Expected: Since the seed is identical, they MUST get the same variation.
        """
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            same_bucketing_seed = "common-seed-123"

            user1_flag = vwo_client.get_flag("featureOne", {
                "id": "KaustubhVWO",
                "bucketingSeed": same_bucketing_seed,
            })

            user2_flag = vwo_client.get_flag("featureOne", {
                "id": "RandomUserVWO",
                "bucketingSeed": same_bucketing_seed,
            })

            self.assertEqual(user1_flag.get_variables(), user2_flag.get_variables())


    def test_should_assign_different_variations_to_users_with_different_bucketing_seeds(self):
        """
        Case 3: Different Seeds
        Scenario: The SAME User ID is used, but with DIFFERENT bucketing seeds.
        Expected: The SDK should bucket based on the seed. Since we use seeds known
        to produce different results ('KaustubhVWO' vs 'RandomUserVWO'), the outcomes should differ.
        """
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            # Same user ID, different seeds
            # Using the names as seeds to simulate the difference
            user1_flag = vwo_client.get_flag("featureOne", {
                "id": "sameId",
                "bucketingSeed": "KaustubhVWO"
            })
            user2_flag = vwo_client.get_flag("featureOne", {
                "id": "sameId",
                "bucketingSeed": "RandomUserVWO"
            })

            self.assertNotEqual(user1_flag.get_variables(), user2_flag.get_variables())

    def test_should_fallback_to_user_id_when_bucketing_seed_is_empty_string(self):
        """
        Case 4: Empty String Seed
        Scenario: bucketingSeed is provided but it's an empty string.
        Expected: Empty string is falsy, so it should fall back to userId.
        Different users should get different variations.
        """
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            # Empty string should be treated as no seed
            user1_flag = vwo_client.get_flag("featureOne", {
                "id": "KaustubhVWO",
                "bucketingSeed": ""
            })
            user2_flag = vwo_client.get_flag("featureOne", {
                "id": "RandomUserVWO",
                "bucketingSeed": ""
            })

            # Should use userIds since empty strings are falsy
            self.assertNotEqual(user1_flag.get_variables(), user2_flag.get_variables())


class TestGetFlagWithCustomSaltAndBucketingSeedCombinations(unittest.TestCase):
    """Test cases for getFlag with custom salt and bucketing seed combinations."""

    sdk_key = "abcdef"
    account_id = "123456"

    def test_no_bucketing_seed_custom_salt_present(self):
        """
        No bucketing seed, custom salt present - 10 users, randomly distributed,
        but each user getting same variation in both flags.
        """
        from tests.data.dummy_test_data_reader import settings_files
        settings_with_same_salt = settings_files.get("SETTINGS_WITH_SAME_SALT")

        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=settings_with_same_salt,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            for i in range(1, 11):
                user_id = f"user{i}"
                flag1 = vwo_client.get_flag("feature1", {"id": user_id})
                flag2 = vwo_client.get_flag("feature2", {"id": user_id})

                # Both flags should yield the exact same variation for the same user due to identical salt
                self.assertEqual(flag1.get_variables(), flag2.get_variables())

    def test_bucketing_seed_present_salt_present(self):
        """
        Bucketing seed present, salt present - 10 users, all users getting same variation in both flags.
        """
        from tests.data.dummy_test_data_reader import settings_files
        settings_with_same_salt = settings_files.get("SETTINGS_WITH_SAME_SALT")

        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=settings_with_same_salt,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            common_bucketing_seed = "common_seed_456"
            variations_assigned = set()
            # loop for 10 users 
            for i in range(1, 11):
                user_id = f"user{i}"
                flag1 = vwo_client.get_flag("feature1", {"id": user_id, "bucketingSeed": common_bucketing_seed})
                flag2 = vwo_client.get_flag("feature2", {"id": user_id, "bucketingSeed": common_bucketing_seed})

                # Both flags should yield the exact same variation
                self.assertEqual(flag1.get_variables(), flag2.get_variables())

                # Using string representation matching Node's JSON.stringify check
                import json
                variations_assigned.add(json.dumps(flag1.get_variables(), sort_keys=True))

            # Since the bucketing seed is the exact same for all 10 users, they MUST all get the same variation
            self.assertEqual(len(variations_assigned), 1)


class TestGetFlagWithForcedVariationAndBucketingSeed(unittest.TestCase):
    """Test cases for getFlag with forced variation (whitelisting) and bucketing seed."""

    sdk_key = "abcdef"
    account_id = "123456"

    def test_should_return_forced_variation_for_whitelisted_user_without_bucketing_seed(self):
        """
        In MOCK_SETTINGS_FILE, 'forcedKaustubh' is whitelisted to Variation-2 (value: 'var2').
        """
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            forced_user_flag = vwo_client.get_flag("featureOne", {"id": "forcedKaustubh"})

            variables = forced_user_flag.get_variables()
            self.assertTrue(any(var.get('value') == 'var2' for var in variables))

    def test_should_still_return_forced_variation_for_whitelisted_user_when_bucketing_seed_is_present(self):
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ):
            options = {"sdk_key": self.sdk_key, "account_id": self.account_id}
            vwo_client = init(options)

            forced_user_flag = vwo_client.get_flag("featureOne", {
                "id": "forcedKaustubh",
                "bucketingSeed": "some-seed-xyz"
            })

            variables = forced_user_flag.get_variables()
            self.assertTrue(any(var.get('value') == 'var2' for var in variables))


class TestGetFlagWithAliasingEnabledAndBucketingSeed(unittest.TestCase):
    """Test cases for getFlag with aliasing enabled and bucketing seed."""

    sdk_key = "abcdef"
    account_id = "123456"

    def test_aliased_users_resolving_to_different_user_ids_should_get_same_variation_with_same_seed(self):
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ), patch(
            "requests.Session.get",
            return_value=mock_response,
        ):
            options = {
                "sdk_key": self.sdk_key,
                "account_id": self.account_id,
                "is_aliasing_enabled": True,
                "gateway_service": {"url": "https://gateway.vwo.com"}
            }
            vwo_client = init(options)
            bucketing_seed = "shared-seed-abc"

            with patch("vwo.vwo_client.get_alias_user_id", side_effect=["RandomUserVWO", "WingifyVWO"]) as mock_alias:
                flag1 = vwo_client.get_flag("featureOne", {
                    "id": "aliasUserA",
                    "bucketingSeed": bucketing_seed
                })
                flag2 = vwo_client.get_flag("featureOne", {
                    "id": "aliasUserB",
                    "bucketingSeed": bucketing_seed
                })

                self.assertEqual(mock_alias.call_count, 2)
                self.assertEqual(flag1.get_variables(), flag2.get_variables())

    def test_aliased_users_resolving_to_different_user_ids_should_get_different_variations_without_seed(self):
        mock_response = MagicMock(status_code=200, headers={"Content-Type": "application/json"}, json=lambda: {})
        with patch(
            "vwo.vwo_builder.VWOBuilder.get_settings",
            return_value=MOCK_SETTINGS_FILE,
        ), patch(
            "vwo.vwo_builder.VWOBuilder.update_poll_interval_and_check_and_poll",
            return_value=None,
        ), patch(
            "requests.Session.post",
            return_value=mock_response,
        ), patch(
            "requests.Session.get",
            return_value=mock_response,
        ):
            options = {
                "sdk_key": self.sdk_key,
                "account_id": self.account_id,
                "is_aliasing_enabled": True,
                "gateway_service": {"url": "https://gateway.vwo.com"}
            }
            vwo_client = init(options)

            with patch("vwo.vwo_client.get_alias_user_id", side_effect=["RandomUserVWO", "WingifyVWO"]) as mock_alias:
                flag1 = vwo_client.get_flag("featureOne", {"id": "aliasUserA"})
                flag2 = vwo_client.get_flag("featureOne", {"id": "aliasUserB"})

                self.assertEqual(mock_alias.call_count, 2)
                self.assertNotEqual(flag1.get_variables(), flag2.get_variables())


if __name__ == "__main__":
    unittest.main()
