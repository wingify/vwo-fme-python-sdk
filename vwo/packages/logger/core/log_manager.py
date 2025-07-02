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


import uuid
from ..enums.log_level_enum import LogLevelEnum
from .log_transport_manager import LogTransportManager
from ..transports.console_transport import ConsoleTransport
from typing import List
from ..logger import Logger
import datetime
from typing import Dict, Any, Union
from ....enums.event_enum import EventEnum
from ....constants.Constants import Constants



class LogManager(Logger):
    _instance = None
    stored_messages = (
        set()
    )  # Set to store already logged messages for duplicate prevention

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Dict[str, Any] = None):
        if "initialized" in self.__dict__:
            return
        self.__dict__["initialized"] = True
        self.config = config or {}
        self.name = self.config.get("name", "VWO Logger")
        self.request_id = self.config.get("requestId", "unique-request-id")
        self.level = self.config.get("level", LogLevelEnum.ERROR)
        self.prefix = self.config.get("prefix", "VWO-SDK")
        self.date_time_format = self.config.get(
            "dateTimeFormat", lambda: datetime.datetime.utcnow().isoformat()
        )
        self.is_ansi_color_enabled = self.config.get("isAnsiColorEnabled", False)

        self.transport_manager = LogTransportManager(self.config)
        self.handle_transports()

    @staticmethod
    def get_instance() -> "LogManager":
        return LogManager()

    def handle_transports(self) -> None:
        transports = self.config.get("transports", [])

        if transports:
            self.add_transports(transports)
        else:
            transport = self.config.get("transport")
            if transport:
                self.add_transport(transport)
            else:
                self.add_transport(
                    ConsoleTransport(
                        {
                            "level": self.level,
                            "isAnsiColorEnabled": self.is_ansi_color_enabled,
                        }
                    )
                )

    def add_transport(self, transport: Union[Logger, Dict[str, Any]]) -> None:
        if isinstance(transport, Dict):
            self.transport_manager.add_transport(ConsoleTransport(transport))
        else:
            self.transport_manager.add_transport(transport)

    def add_transports(self, transports: List[Union[Logger, Dict[str, Any]]]) -> None:
        for transport in transports:
            self.add_transport(transport)

    def trace(self, message: str) -> None:
        self.transport_manager.log(LogLevelEnum.TRACE, message)

    def debug(self, message: str) -> None:
        self.transport_manager.log(LogLevelEnum.DEBUG, message)

    def info(self, message: str) -> None:
        self.transport_manager.log(LogLevelEnum.INFO, message)

    def warn(self, message: str) -> None:
        self.transport_manager.log(LogLevelEnum.WARN, message)

    def error(self, message: str) -> None:
        from ....utils.log_message_util import send_log_to_vwo

        # Log the error using the transport manager
        self.transport_manager.log(LogLevelEnum.ERROR, message)
        send_log_to_vwo(message, LogLevelEnum.ERROR)
