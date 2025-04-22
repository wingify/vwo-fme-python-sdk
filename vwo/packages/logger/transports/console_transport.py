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


from ..logger import Logger
from ..enums.log_level_enum import LogLevelEnum
from typing import Any, Dict


class ConsoleTransport(Logger):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.level = self.config.get("level", LogLevelEnum.ERROR)
        self.is_ansi_color_enabled = self.config.get("isAnsiColorEnabled", False)

    def trace(self, message: str) -> None:
        self.console_log(message)

    def debug(self, message: str) -> None:
        self.console_log(message)

    def info(self, message: str) -> None:
        self.console_log(message)

    def warn(self, message: str) -> None:
        self.console_log(message)

    def error(self, message: str) -> None:
        self.console_log(message)

    def console_log(self, message: str) -> None:
        print(message)
