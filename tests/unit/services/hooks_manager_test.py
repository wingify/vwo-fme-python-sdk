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

"""Unit tests for integrations callback error handling in ``HooksManager``."""

import unittest
from unittest.mock import patch

from wingify.packages.logger.core.log_manager import LogManager
from wingify.services.hooks_manager import HooksManager


class HooksManagerTest(unittest.TestCase):
    """Tests for ``HooksManager.execute`` integrations callback behavior."""

    def setUp(self):
        """
        Initialize logger for tests that assert on ``error_log`` output.

        :return: None.
        """
        LogManager({"level": "ERROR"})

    def test_execute_logs_integrations_callback_failure_without_raising(self):
        """
        Verify callback exceptions are logged and do not propagate to the caller.

        Ensures ``getFlag`` / ``trackEvent`` continue after an integrations failure
        with a clear ``INTEGRATIONS_CALLBACK_FAILED`` message.

        :return: None. Asserts error log key and message content.
        """
        def failing_callback(_properties):
            # Simulates user-thrown error inside integrations callback
            raise RuntimeError("callback exploded")

        manager = HooksManager(
            {"integrations": {"callback": failing_callback}}
        )

        with patch.object(
            LogManager.get_instance(), "error_log"
        ) as mock_error_log:
            # Must not raise — API flow should continue
            manager.execute({"api": "getFlag", "featureKey": "feature1"})

        mock_error_log.assert_called_once()
        self.assertEqual(mock_error_log.call_args[0][0], "INTEGRATIONS_CALLBACK_FAILED")
        self.assertIn("callback exploded", mock_error_log.call_args[1]["data"]["err"])

    def test_execute_runs_successful_callback(self):
        """
        Verify a valid integrations callback receives properties and runs normally.

        :return: None. Asserts callback payload is passed through unchanged.
        """
        received = {}

        def callback(properties):
            received.update(properties)

        manager = HooksManager({"integrations": {"callback": callback}})
        manager.execute({"api": "trackEvent", "event_name": "clickElement"})

        self.assertEqual(received["event_name"], "clickElement")


if __name__ == "__main__":
    unittest.main()
