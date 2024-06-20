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


from typing import Dict, Any, Optional
from .packages.network_layer.manager.network_manager import NetworkManager
from .services.settings_manager import SettingsManager
from .vwo_client import VWOClient
import random
import json
import threading
from .packages.logger.core.log_manager import LogManager
from .utils.log_message_util import debug_messages, error_messages, info_messages
from .packages.segmentation_evaluator.core.segmentation_manager import (
    SegmentationManager,
)
from .utils.settings_util import set_settings_and_add_campaigns_to_rules
from .packages.storage.storage import Storage


class VWOBuilder:
    def __init__(self, options):
        self.sdk_key = options["sdk_key"]
        self.options = options
        self.settings = None
        self.storage = None
        self.log_manager = None
        self.original_settings = None
        self.is_settings_fetch_in_progress = False
        self.vwo_instance = None

    def set_network_manager(self):
        NetworkManager.get_instance().attach_client()
        LogManager.get_instance().debug(
            debug_messages.get("SERVICE_INITIALIZED").format(service="Network Layer")
        )
        NetworkManager.get_instance().get_config().set_development_mode(
            self.options.get("isDevelopmentMode", False)
        )
        return self

    def set_segmentation(self):
        SegmentationManager.get_instance().attach_evaluator(
            self.options.get("segmentation", None)
        )
        LogManager.get_instance().debug(
            debug_messages.get("SERVICE_INITIALIZED").format(
                service="Segmentation Evaluator"
            )
        )
        return self

    def fetch_settings(self, force=False):
        if not self.sdk_key or not self.options.get("account_id"):
            raise ValueError(
                "sdk_key and account_id are required for fetching settings. Aborting!"
            )

        if not self.is_settings_fetch_in_progress:
            self.is_settings_fetch_in_progress = True
            try:
                settings = self.setting_file_manager.get_settings(force)
                if not force:
                    self.original_settings = settings

                self.is_settings_fetch_in_progress = False
                return settings
            except Exception as err:
                self.is_settings_fetch_in_progress = False
                raise err

    def get_settings(self, force=False):
        try:
            if not force and self.settings:
                LogManager.get_instance().info(
                    "Using already fetched and cached settings"
                )
                return self.settings
            else:
                return self.fetch_settings(force)
        except Exception as err:
            LogManager.get_instance().error(
                "Failed to fetch settings. Error: " + str(err)
            )
            return {}

    def set_storage(self):
        if self.options.get("storage"):
            self.storage = Storage.get_instance().attach_connector(
                self.options.get("storage")
            )
            LogManager.get_instance().debug(
                debug_messages.get("SERVICE_INITIALIZED").format(service="Storage")
            )
        return self

    def set_settings_manager(self):
        self.setting_file_manager = SettingsManager(self.options)
        return self

    def set_logger(self):
        self.log_manager = LogManager(self.options.get("logger", {}))
        LogManager.get_instance().debug(
            debug_messages.get("SERVICE_INITIALIZED").format(service="Logger")
        )
        return self

    def get_random_user_id(self):
        apiName = "getRandomUserId"
        try:
            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=apiName)
            )
            return str(random.uuid4())
        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=apiName, err=str(err)
                )
            )

    def init_polling(self):
        if not self.options.get("poll_interval"):
            return self

        poll_interval = self.options.get("poll_interval")
        if poll_interval and isinstance(poll_interval, int) and poll_interval >= 1000:
            self.check_and_poll(poll_interval)
        else:
            LogManager.get_instance().error(
                error_messages.get("INIT_OPTIONS_INVALID").format(
                    key="poll_interval", correctType="int >= 1000"
                )
            )
        return self

    def build(self, settings):
        self.vwo_instance = VWOClient(settings, self.options)
        return self.vwo_instance

    def check_and_poll(self, poll_interval):
        def poll():
            try:
                latest_settings = self.get_settings(True)
                if json.dumps(latest_settings, sort_keys=True) != json.dumps(
                    self.original_settings, sort_keys=True
                ):
                    self.original_settings = latest_settings
                    LogManager.get_instance().info(
                        info_messages.get("POLLING_SET_SETTINGS")
                    )
                    set_settings_and_add_campaigns_to_rules(
                        latest_settings, self.vwo_instance
                    )
                else:
                    LogManager.get_instance().info(
                        info_messages.get("POLLING_NO_CHANGE_IN_SETTINGS")
                    )
            except Exception as e:
                LogManager.get_instance().error(
                    error_messages.get("POLLING_FETCH_SETTINGS_FAILED")
                )
            finally:
                # Reschedule the poll function to be called again after the interval
                threading.Timer(
                    poll_interval / 1000, poll
                ).start()  # Timer expects seconds, so convert milliseconds

        # start the polling after given interval
        threading.Timer(poll_interval / 1000, poll).start()
