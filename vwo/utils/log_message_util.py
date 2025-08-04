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


import re
import json
import os
from typing import Dict, Any
from ..enums.event_enum import EventEnum
from ..constants.Constants import Constants

# Determine the base directory (the directory containing this script)
base_dir = os.path.dirname(__file__)

# Set to store already logged messages (to avoid duplicates)
stored_messages = set()


def load_json_file(filename: str) -> Dict[str, str]:
    """
    Loads a JSON file and returns its content as a dictionary.

    :param filename: The name of the JSON file to load.
    :return: A dictionary with the contents of the JSON file.
    """
    filepath = os.path.join(base_dir, "../resources", filename)
    with open(filepath, "r") as file:
        return json.load(file)


# Load all required JSON files
debug_messages = load_json_file("debug-messages.json")
error_messages = load_json_file("error-messages.json")
info_messages = load_json_file("info-message.json")
trace_messages = load_json_file("trace-messages.json")
warn_messages = load_json_file("warn-messages.json")


def send_log_to_vwo(message: str, message_type: str) -> None:
    """
    Sends a log message to VWO.

    :param message: The message to send.
    :param message_type: The type of message (e.g., ERROR, INFO).
    """
    from ..utils.network_util import (
        get_events_base_properties,
        get_messaging_event_payload,
        send_event,
    )

    if os.getenv("TEST_ENV") == "true":
        return  # Skip logging in test environment

    # Construct the message to check for duplicates
    message_to_send = f"{message}-{Constants.SDK_NAME}-{Constants.SDK_VERSION}"

    # Avoid sending duplicate messages
    if message_to_send not in stored_messages:
        # Add the message to the stored set to prevent duplicates
        stored_messages.add(message_to_send)

        # Get event properties for the error event
        properties = get_events_base_properties(EventEnum.VWO_LOG_EVENT.value)

        # Create the payload for the messaging event
        payload = get_messaging_event_payload(
            message_type, message, EventEnum.VWO_LOG_EVENT.value
        )

        # Send the message via HTTP request
        send_event(properties, payload, EventEnum.VWO_LOG_EVENT.value)