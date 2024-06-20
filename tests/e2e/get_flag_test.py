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
from vwo import init
from ..data.dummy_test_data_reader import settings_files, test_data
from typing import Dict, List, Any
from ..data.user_storage import user_storage


class VWOTest(unittest.TestCase):

    sdk_key = "abcd"
    account_id = "1234"

    def test_01_get_flag_without_storage(self):
        self._helper_function_to_run_test(
            test_data.get("GETFLAG_WITHOUT_STORAGE"), False
        )

    def test_02_get_flag_with_meg_random(self):
        self._helper_function_to_run_test(test_data.get("GETFLAG_MEG_RANDOM"), False)

    def test_03_get_flag_with_meg_advance(self):
        self._helper_function_to_run_test(test_data.get("GETFLAG_MEG_ADVANCE"), False)

    def test_04_get_flag_with_storage(self):
        self._helper_function_to_run_test(test_data.get("GETFLAG_WITH_STORAGE"), True)

    def _helper_function_to_run_test(
        self, test_data: List[Dict[str, Any]], is_storage: bool
    ):
        for data in test_data:
            with patch(
                "vwo.vwo_builder.VWOBuilder.get_settings",
                return_value=settings_files.get(data.get("settings")),
            ) as mock_get_settings:
                storage = user_storage()
                options = {"sdk_key": self.sdk_key, "account_id": self.account_id}

                if is_storage:
                    options["storage"] = storage

                vwo_instance = init(options)

                if is_storage:
                    storage_data = storage.get(
                        data["featureKey"], data["context"]["id"]
                    )
                    self.assertIsNone(storage_data)

                feature_flag = vwo_instance.get_flag(
                    data["featureKey"], data["context"]
                )
                self.assertEqual(
                    data["expectation"]["isEnabled"], feature_flag.is_enabled()
                )
                self.assertEqual(
                    data["expectation"]["intVariable"],
                    feature_flag.get_variable("int", 1),
                )
                self.assertEqual(
                    data["expectation"]["stringVariable"],
                    feature_flag.get_variable("string", "VWO"),
                    data["settings"] + " " + data["description"],
                )
                self.assertEqual(
                    data["expectation"]["floatVariable"],
                    feature_flag.get_variable("float", 1.1),
                )
                self.assertEqual(
                    data["expectation"]["booleanVariable"],
                    feature_flag.get_variable("boolean", False),
                )
                self.assertEqual(
                    data["expectation"]["jsonVariable"],
                    feature_flag.get_variable("json", {}),
                )

                if is_storage:
                    if data["expectation"]["isEnabled"]:
                        updated_storage_data = storage.get(
                            data["featureKey"], data["context"]["id"]
                        )
                        self.assertEqual(
                            data["expectation"]["storageData"].get("rolloutKey", None),
                            updated_storage_data["rolloutKey"],
                        )
                        self.assertEqual(
                            data["expectation"]["storageData"].get(
                                "rolloutVariationId", None
                            ),
                            updated_storage_data["rolloutVariationId"],
                        )
                        self.assertEqual(
                            data["expectation"]["storageData"].get(
                                "experimentKey", None
                            ),
                            updated_storage_data["experimentKey"],
                        )
                        self.assertEqual(
                            data["expectation"]["storageData"].get(
                                "experimentVariationId", None
                            ),
                            updated_storage_data["experimentVariationId"],
                        )


if __name__ == "__main__":
    unittest.main()
