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

"""Unit tests for ``WingifyClient._validate_context`` user ID validation."""

import unittest
from unittest.mock import patch

from wingify.packages.logger.core.log_manager import LogManager
from wingify.wingify_client import WingifyClient


class WingifyClientValidationTest(unittest.TestCase):
    """Tests for context ``id`` type validation before UUID generation."""

    def setUp(self):
        """
        Create a bare ``WingifyClient`` instance without running full SDK init.

        :return: None.
        """
        LogManager({"level": "ERROR"})
        # Skip __init__ — only _validate_context is under test
        self.client = object.__new__(WingifyClient)

    def test_validate_context_rejects_integer_user_id(self):
        """
        Verify integer ``context['id']`` raises ``ValueError`` with a clear message.

        Logs ``INVALID_CONTEXT_USER_ID`` before raising so developers see a clear validation error.

        :return: None. Asserts exception message and that error was logged.
        """
        with patch.object(LogManager.get_instance(), "error") as mock_error:
            with self.assertRaises(ValueError) as ctx:
                self.client._validate_context({"id": 123}, "getFlag")

        self.assertIn("string value", str(ctx.exception))
        mock_error.assert_called_once()

    def test_validate_context_accepts_string_user_id(self):
        """
        Verify string ``context['id']`` passes validation without error.

        :return: None. Asserts no exception is raised.
        """
        # Should complete without raising
        self.client._validate_context({"id": "user-123"}, "getFlag")

    def test_validate_context_rejects_missing_id(self):
        """
        Verify missing ``id`` in context raises ``ValueError``.

        :return: None. Asserts ``ValueError`` is raised for empty context.
        """
        with self.assertRaises(ValueError):
            self.client._validate_context({}, "trackEvent")


if __name__ == "__main__":
    unittest.main()
