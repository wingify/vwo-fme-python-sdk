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

import json
import os
from typing import Dict

from ..constants.Constants import Constants
from ..enums.event_enum import EventEnum
from ..utils.brand_util import get_brand, get_log_prefix

base_dir = os.path.dirname(__file__)
stored_messages = set()

debug_messages: Dict[str, str] = {}
error_messages: Dict[str, str] = {}
info_messages: Dict[str, str] = {}
trace_messages: Dict[str, str] = {}
warn_messages: Dict[str, str] = {}


def _apply_brand_tokens(message: str, is_via_vwo: bool) -> str:
    return (
        message.replace("{log_prefix}", get_log_prefix(is_via_vwo))
        .replace("{brand}", get_brand(is_via_vwo))
    )


def load_json_file(filename: str, is_via_vwo: bool) -> Dict[str, str]:
    filepath = os.path.join(base_dir, "../resources", filename)
    with open(filepath, "r") as file:
        raw = json.load(file)
    return {key: _apply_brand_tokens(value, is_via_vwo) for key, value in raw.items()}


def refresh_log_messages(is_via_vwo: bool) -> None:
    """Reload templated log messages for the active brand (called at SDK init)."""
    loaded = {
        "debug": load_json_file("debug-messages.json", is_via_vwo),
        "error": load_json_file("error-messages.json", is_via_vwo),
        "info": load_json_file("info-message.json", is_via_vwo),
        "trace": load_json_file("trace-messages.json", is_via_vwo),
        "warn": load_json_file("warn-messages.json", is_via_vwo),
    }
    for target, source in (
        (debug_messages, loaded["debug"]),
        (error_messages, loaded["error"]),
        (info_messages, loaded["info"]),
        (trace_messages, loaded["trace"]),
        (warn_messages, loaded["warn"]),
    ):
        target.clear()
        target.update(source)


# Default messages before init (Wingify brand).
refresh_log_messages(False)


def send_log_to_vwo(message: str, message_type: str) -> None:
    from ..utils.network_util import (
        get_events_base_properties,
        get_messaging_event_payload,
        send_event,
    )
    from ..utils.brand_context import get_is_via_vwo
    from ..services.settings_manager import SettingsManager

    if os.getenv("TEST_ENV") == "true":
        return

    sdk_name = Constants.WINGIFY_SDK_NAME
    settings = SettingsManager.get_instance()
    if settings is not None:
        sdk_name = settings.get_sdk_name()

    message_to_send = f"{message}-{sdk_name}-{Constants.SDK_VERSION}"
    if message_to_send not in stored_messages:
        stored_messages.add(message_to_send)
        properties = get_events_base_properties(EventEnum.LOG_EVENT.value)
        payload = get_messaging_event_payload(
            message_type, message, EventEnum.LOG_EVENT.value
        )
        send_event(properties, payload, EventEnum.LOG_EVENT.value)
