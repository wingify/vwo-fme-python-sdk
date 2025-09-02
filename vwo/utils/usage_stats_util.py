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

from typing import Dict, Any, Union
import sys
from ..constants.Constants import Constants
from ..packages.logger.enums.log_level_number_enum import LogLevelNumberEnum
from ..services.settings_manager import SettingsManager

class UsageStatsUtil:
    """
    Manages usage statistics for the SDK.
    Tracks various features and configurations being used by the client.
    Implements Singleton pattern to ensure a single instance.
    """

    _instance = None

    def __new__(cls):
        """
        Ensures only one instance of UsageStatsUtil exists (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(UsageStatsUtil, cls).__new__(cls)
            cls._instance._usage_stats_data = {}
        return cls._instance

    def set_usage_stats(self, options: Dict[str, Any]) -> None:
        """
        Sets usage statistics based on provided options.
        Maps various SDK features and configurations to boolean flags.

        Args:
            options (Dict[str, Any]): Configuration options for the SDK containing:
                - storage: Storage service configuration
                - logger: Logger configuration
                - batch_event_data: Event batching configuration
                - integrations: Integrations configuration
                - polling_interval: Polling interval configuration
                - sdk_name: SDK name configuration
        """
        data: Dict[str, Union[str, int]] = {}
        data["a"] = SettingsManager.get_instance().get_account_id()
        data["env"] = SettingsManager.get_instance().get_sdk_key()

        # Map configuration options to usage stats flags
        if options.get("integrations"):
            data["ig"] = 1  # Integration enabled
        if options.get("batch_event_data"):
            data["eb"] = 1  # Event batching enabled

        if options.get("gateway_service"):
            data["gs"] = 1  # Gateway service enabled

        # Check for custom logger
        logger = options.get("logger")
        if logger and (logger.get("transport") or logger.get("transports")):
            data["cl"] = 1

        if options.get("storage"):
            data["ss"] = 1  # Storage service configured

        if logger and logger.get("level"):
            data["ll"] = getattr(
                LogLevelNumberEnum, logger["level"].upper(), LogLevelNumberEnum.ERROR
            )  # Default to -1 if level is not recognized

        if options.get("poll_interval"):
            data["pi"] = 1  # Polling interval configured

        # Check for _vwo_meta.ea
        vwo_meta = options.get("_vwo_meta")
        if vwo_meta and vwo_meta.get("ea"):
            data["_ea"] = 1

        # Add Python version if available
        if hasattr(sys, "version"):
            data["lv"] = sys.version

        # Check threading configuration
        threading_config = options.get("threading")
        if not threading_config or (
            threading_config and threading_config.get("enabled") is True
        ):
            data["th"] = 1
            # Check if max_workers is passed
            if threading_config and threading_config.get("max_workers"):
                data["th_mps"] = threading_config["max_workers"]

        self._usage_stats_data = data

    def get_usage_stats(self) -> Dict[str, Union[bool, str, int]]:
        """
        Retrieves the current usage statistics.

        Returns:
            Dict[str, Union[bool, str, int]]: Dictionary containing boolean flags for various SDK features in use
        """
        return self._usage_stats_data

    def clear_usage_stats(self) -> None:
        """
        Clears the usage statistics data.
        """
        self._usage_stats_data = {}
