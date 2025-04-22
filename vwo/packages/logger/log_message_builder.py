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


from .enums.log_level_enum import LogLevelEnum
from typing import Any, Dict
import datetime


class LogMessageBuilder:
    ANSI_COLOR_ENUM = {
        "BOLD": "\033[1m",
        "CYAN": "\033[36m",
        "GREEN": "\033[32m",
        "LIGHTBLUE": "\033[94m",
        "RED": "\033[31m",
        "RESET": "\033[0m",
        "WHITE": "\033[97m",  # Bright white
        "YELLOW": "\033[33m",
    }

    def __init__(self, logger_config: Dict[str, Any], transport_config: Dict[str, Any]):
        self.logger_config = logger_config
        self.transport_config = transport_config
        self.prefix = self.transport_config.get(
            "prefix", self.logger_config.get("prefix", "VWO-SDK")
        )
        self.date_time_format = self.transport_config.get(
            "dateTimeFormat",
            self.logger_config.get("dateTimeFormat", self.default_date_time_format),
        )
        # Determine if ANSI color is enabled
        self.is_ansi_color_enabled = self.logger_config.get("isAnsiColorEnabled", False)

    def format_message(self, level: str, message: str) -> str:
        color_code = self.get_color_code(level) if self.is_ansi_color_enabled else ""
        reset_code = "\033[0m" if self.is_ansi_color_enabled else ""
        timestamp = self.get_formatted_date_time()
        return f"{color_code}[{level.upper()}] {self.prefix} {reset_code}{timestamp} {message}"

    def get_color_code(self, level: str) -> str:
        color_map = {
            LogLevelEnum.TRACE: "\033[37m",  # White
            LogLevelEnum.DEBUG: "\033[94m",  # Light Blue
            LogLevelEnum.INFO: "\033[36m",  # Cyan
            LogLevelEnum.WARN: "\033[33m",  # Yellow
            LogLevelEnum.ERROR: "\033[31m",  # Red
        }
        return color_map.get(level, "\033[0m")  # Default to reset if level not found

    def get_formatted_date_time(self) -> str:
        return self.date_time_format()

    def default_date_time_format(self) -> str:
        return datetime.datetime.utcnow().isoformat()
