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


from typing import Any, Dict
from ..enums.event_enum import EventEnum


def send_debug_event_to_vwo(debug_event_props: Dict[str, Any]):
    """
    Sends a debug event to VWO.

    :param debug_event_props: The properties of the debug event.
    """
    try:
        # Lazy import to avoid circular dependency with LogManager
        from ..utils.network_util import (
            get_events_base_properties,
            get_debugger_event_payload,
            send_event,
        )
        # Create the query parameters
        properties = get_events_base_properties(EventEnum.VWO_DEBUGGER_EVENT.value)
        # Create the payload with required fields
        payload = get_debugger_event_payload(debug_event_props)

        # Send the constructed payload via POST request
        send_event(properties, payload, EventEnum.VWO_DEBUGGER_EVENT.value)
    except Exception as e:
        from ..packages.logger.core.log_manager import LogManager
        LogManager.get_instance().error_log("ERROR_SENDING_DEBUG_EVENT", data={"err": str(e)}, debug_data=debug_event_props)