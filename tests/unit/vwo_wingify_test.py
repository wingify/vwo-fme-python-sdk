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

import importlib
import unittest
import unittest.mock

from wingify.utils.brand_util import (
    get_brand,
    get_events_hostname,
    get_log_prefix,
    get_sdk_name,
    get_settings_hostname,
)
from wingify.utils.brand_context import set_is_via_vwo
from wingify.utils.log_message_util import refresh_log_messages, info_messages


class RuntimeBrandTest(unittest.TestCase):
    """Brand is selected at init via is_via_vwo"""

    def test_vwo_runtime_brand(self):
        set_is_via_vwo(True)
        refresh_log_messages(True)
        self.assertEqual(get_sdk_name(True), "vwo-fme-python-sdk")
        self.assertEqual(get_settings_hostname(True), "dev.visualwebsiteoptimizer.com")
        self.assertEqual(get_events_hostname(True), "dev.visualwebsiteoptimizer.com")
        self.assertEqual(get_log_prefix(True), "VWO-SDK")
        self.assertEqual(get_brand(True), "VWO")

    def test_wingify_runtime_brand(self):
        set_is_via_vwo(False)
        refresh_log_messages(False)
        self.assertEqual(get_sdk_name(False), "wingify-fme-python-sdk")
        self.assertEqual(get_settings_hostname(False), "edge.wingify.net")
        self.assertEqual(get_events_hostname(False), "collect.wingify.net")
        self.assertEqual(get_log_prefix(False), "Wingify-SDK")
        self.assertEqual(get_brand(False), "Wingify")

    def test_log_messages_use_runtime_brand(self):
        refresh_log_messages(True)
        sample = next(iter(info_messages.values()))
        self.assertIn("VWO-SDK", sample)


class VwoFacadeTest(unittest.TestCase):
    """Legacy VWO types must alias the Wingify core (same class objects)."""

    def test_vwo_client_is_wingify_client(self):
        from vwo.vwo_client import VWOClient
        from wingify.wingify_client import WingifyClient

        self.assertIs(VWOClient, WingifyClient)

    def test_vwo_builder_is_wingify_builder(self):
        from vwo.vwo_builder import VWOBuilder
        from wingify.wingify_builder import WingifyBuilder

        self.assertIs(VWOBuilder, WingifyBuilder)

    def test_vwo_options_model_is_wingify_options_model(self):
        from vwo.models.vwo_options_model import VWOOptionsModel
        from wingify.models.wingify_options_model import WingifyOptionsModel

        self.assertIs(VWOOptionsModel, WingifyOptionsModel)

    def test_vwo_init_sets_is_via_vwo(self):
        from vwo.vwo import init as vwo_init
        from wingify.wingify import init as wingify_init

        self.assertIsNot(vwo_init, wingify_init)
        with unittest.mock.patch("wingify.wingify.Wingify.set_instance") as mock_set:
            mock_set.return_value = None
            vwo_init({"sdk_key": "k", "account_id": "1"})
            options = mock_set.call_args[0][0]
            self.assertTrue(options["is_via_vwo"])

    def test_settings_manager_respects_is_via_vwo(self):
        from wingify.services.settings_manager import SettingsManager

        sm = SettingsManager({"sdk_key": "k", "account_id": "1", "is_via_vwo": True})
        self.assertEqual(sm.get_sdk_name(), "vwo-fme-python-sdk")
        self.assertEqual(sm.settings_hostname, "dev.visualwebsiteoptimizer.com")

        sm2 = SettingsManager({"sdk_key": "k", "account_id": "1", "is_via_vwo": False})
        self.assertEqual(sm2.get_sdk_name(), "wingify-fme-python-sdk")
        self.assertEqual(sm2.settings_hostname, "edge.wingify.net")


class WingifyOptionsModelTest(unittest.TestCase):
    """Dual meta and builder key support."""

    def test_vwo_meta_fallback(self):
        from wingify.models.wingify_options_model import WingifyOptionsModel

        model = WingifyOptionsModel({"_vwo_meta": {"_vwo_sdkName": "custom-sdk"}})
        self.assertEqual(model.get_sdk_name(), "custom-sdk")
        self.assertEqual(model.get_vwo_meta(), {"_vwo_sdkName": "custom-sdk"})

    def test_wingify_meta_preferred(self):
        from wingify.models.wingify_options_model import WingifyOptionsModel

        model = WingifyOptionsModel(
            {
                "_wingify_meta": {"_wingify_sdkName": "wingify-custom"},
                "_vwo_meta": {"_vwo_sdkName": "vwo-custom"},
            }
        )
        self.assertEqual(model.get_sdk_name(), "wingify-custom")

    def test_vwo_builder_fallback(self):
        from wingify.models.wingify_options_model import WingifyOptionsModel

        builder = object()
        model = WingifyOptionsModel({"vwoBuilder": builder})
        self.assertIs(model.get_wingify_builder(), builder)


class WingifyPackageExportsTest(unittest.TestCase):
    def test_wingify_public_exports(self):
        import wingify

        for name in wingify.__all__:
            self.assertTrue(hasattr(wingify, name), f"Missing export: {name}")


class VwoPackageExportsTest(unittest.TestCase):
    def test_vwo_public_exports(self):
        import vwo

        for name in vwo.__all__:
            self.assertTrue(hasattr(vwo, name), f"Missing export: {name}")


class JavaStyleLayoutTest(unittest.TestCase):
    """Core lives under wingify/; vwo/ holds facade files only."""

    def test_core_api_under_wingify(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[2]
        self.assertTrue((root / "wingify" / "api" / "get_flag_api.py").exists())
        self.assertTrue((root / "wingify" / "constants" / "Constants.py").exists())

    def test_vwo_has_facades_only(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[2]
        vwo_py_files = list((root / "vwo").rglob("*.py"))
        self.assertLessEqual(len(vwo_py_files), 10)
        self.assertFalse((root / "vwo" / "services").exists())
        self.assertFalse((root / "vwo" / "constants").exists())


if __name__ == "__main__":
    unittest.main()
