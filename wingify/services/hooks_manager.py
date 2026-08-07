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


from typing import Callable, Dict, Any, Optional
from ..packages.logger.core.log_manager import LogManager


class HooksManager:
    def __init__(self, options: Dict[str, Any]):
        """
        Initialize the HooksManager with the given options.

        :param options: A dictionary containing configuration options.
        """
        self.callback: Optional[Callable[[Dict[str, Any]], None]] = options.get(
            "integrations", {}
        ).get("callback")
        self.is_callback_function = callable(self.callback)
        self.decision: Dict[str, Any] = {}

    def execute(self, properties: Dict[str, Any]) -> None:
        """
        Executes the callback if it's a valid function.

        :param properties: A dictionary of properties to pass to the callback.
        """
        if self.is_callback_function and self.callback:
            try:
                self.callback(properties)
            except Exception as err:
                LogManager.get_instance().error_log(
                    "INTEGRATIONS_CALLBACK_FAILED",
                    data={"err": str(err)},
                    debug_data={"an": properties.get("api")},
                    should_send_log_to_vwo=False,
                )

    def set(self, properties: Dict[str, Any]) -> None:
        """
        Sets properties to the decision object if the callback is a function.

        :param properties: A dictionary of properties to set.
        """
        if self.is_callback_function:
            self.decision = properties

    def get(self) -> Dict[str, Any]:
        """
        Retrieves the decision object.

        :return: The decision object as a dictionary.
        """
        return self.decision
