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

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from vwo.services.settings_manager import SettingsManager
from tests.data.dummy_test_data_reader import settings_files

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

class SettingsSchemaValidationTest(unittest.TestCase):
    """Test suite for settings schema validation."""
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear all mocks before each test
        self.settings_manager = None
        # Mock LogManager
        self.log_manager_mock = MagicMock()
        self.log_manager_instance_mock = MagicMock()
        self.log_manager_mock.get_instance.return_value = self.log_manager_instance_mock
        with patch('vwo.services.settings_manager.LogManager', self.log_manager_mock):
            self.settings_manager = SettingsManager({
                "account_id": 123,
                "sdk_key": "123"
            })

    def test_settings_with_wrong_type_for_values_should_fail_validation(self):
        """Test that settings with wrong type for values should fail validation."""
        settings = settings_files.get("SETTINGS_WITH_WRONG_TYPE_FOR_VALUES")
        result = SettingsManager.is_settings_valid(settings)
        self.assertFalse(result)

    def test_settings_with_extra_key_at_root_level_should_not_fail_validation(self):
        """Test that settings with extra key at root level should not fail validation."""
        settings = settings_files.get("SETTINGS_WITH_EXTRA_KEYS_AT_ROOT_LEVEL")
        result = SettingsManager.is_settings_valid(settings)
        self.assertTrue(result)

    def test_settings_with_extra_key_inside_objects_should_not_fail_validation(self):
        """Test that settings with extra key inside objects should not fail validation."""
        settings = settings_files.get("SETTINGS_WITH_EXTRA_KEYS_INSIDE_OBJECTS")
        result = SettingsManager.is_settings_valid(settings)
        self.assertTrue(result)

    def test_settings_with_no_feature_and_campaign_should_not_fail_validation(self):
        """Test that settings with no feature and campaign should not fail validation."""
        settings = settings_files.get("SETTINGS_WITH_NO_FEATURES_AND_CAMPAIGNS")
        result = SettingsManager.is_settings_valid(settings)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
