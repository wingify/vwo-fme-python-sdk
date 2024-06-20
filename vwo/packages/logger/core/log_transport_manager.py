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


from ..enums.log_level_number_enum import LogLevelNumberEnum
from ..enums.log_level_enum import LogLevelEnum
from ..logger import Logger
from ..log_message_builder import LogMessageBuilder
from typing import Any, Dict

class LogTransportManager:
    def __init__(self, config: Dict[str, Any]):
        self.transports = []
        self.config = config

    def add_transport(self, transport: Logger) -> None:
        self.transports.append(transport)

    def should_log(self, transport_level: str, config_level: str) -> bool:
        target_level = getattr(LogLevelNumberEnum, transport_level.upper(), LogLevelNumberEnum.ERROR)
        desired_level = getattr(LogLevelNumberEnum, config_level.upper(), LogLevelNumberEnum.ERROR)
        return target_level >= desired_level

    def log(self, level: str, message: str) -> None:
        for transport in self.transports:
            if self.should_log(level, transport.level):
                log_message_builder = LogMessageBuilder(self.config, transport.config)
                formatted_message = log_message_builder.format_message(level, message)
                if hasattr(transport, level):
                    getattr(transport, level)(formatted_message)
