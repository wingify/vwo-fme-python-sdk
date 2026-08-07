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

"""Unit tests for SDK error message templates."""

import unittest

from wingify.utils.log_message_util import error_messages


class LogMessageTest(unittest.TestCase):
    """Tests for ``error-messages.json`` template strings."""

    def test_event_not_found_message_includes_api_name_guidance(self):
        """
        Verify ``EVENT_NOT_FOUND`` guides users to use the event API name.

        When ``trackEvent`` is called with a display name (e.g. ``click_element``)
        instead of the API name (``clickElement``), the log should include API-name guidance.

        :return: None. Asserts event name and API-name guidance appear in message.
        """
        message = error_messages["EVENT_NOT_FOUND"].format(eventName="click_element")
        self.assertIn("click_element", message)
        self.assertIn(
            "please ensure event API name is being used correctly", message
        )

    def test_invalid_context_user_id_message(self):
        """
        Verify ``INVALID_CONTEXT_USER_ID`` uses the expected error wording.

        :return: None. Asserts exact template string matches expected message.
        """
        self.assertEqual(
            error_messages["INVALID_CONTEXT_USER_ID"],
            "user_id under context must be a string value",
        )

    def test_integrations_callback_failed_message_includes_error(self):
        """
        Verify ``INTEGRATIONS_CALLBACK_FAILED`` includes callback context and error detail.

        :return: None. Asserts formatted message contains callback label and error text.
        """
        message = error_messages["INTEGRATIONS_CALLBACK_FAILED"].format(
            err="boom"
        )
        self.assertIn("integrations_callback", message)
        self.assertIn("boom", message)


if __name__ == "__main__":
    unittest.main()
