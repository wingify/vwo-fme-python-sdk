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
import random
from ..packages.network_layer.manager.network_manager import NetworkManager
from ..packages.network_layer.models.request_model import RequestModel
from ..constants.Constants import Constants
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import debug_messages, info_messages, error_messages
from ..models.schemas.settings_schema import SETTINGS_FILE_SCHEMA
import json
import requests
import jsonschema
import time


class SettingsManager:
    _instance = None

    def __init__(self, options):
        self.sdk_key = options["sdk_key"]
        self.account_id = options["account_id"]
        self.expiry = Constants.SETTINGS_EXPIRY
        self.network_timeout = Constants.SETTINGS_TIMEOUT
        self.is_gateway_service_provided = False
        self.settings_fetch_time = None  # time taken to fetch the settings
        self.is_settings_valid_on_init = False

        if "gateway_service" in options and "url" in options["gateway_service"]:
            self.is_gateway_service_provided = True

            # check if url start if https:// or http://
            if options["gateway_service"]["url"].startswith("http://") or options[
                "gateway_service"
            ]["url"].startswith("https://"):
                parsed_url = requests.utils.urlparse(options["gateway_service"]["url"])
            elif "protocol" in options["gateway_service"] and options[
                "gateway_service"
            ]["protocol"] in ["http", "https"]:
                parsed_url = requests.utils.urlparse(
                    options["gateway_service"]["protocol"]
                    + "://"
                    + options["gateway_service"]["url"]
                )
            else:
                parsed_url = requests.utils.urlparse(
                    "https://" + options["gateway_service"]["url"]
                )

            self.hostname = parsed_url.hostname
            self.protocol = parsed_url.scheme
            if parsed_url.port:
                self.port = parsed_url.port
            elif "port" in options["gateway_service"]:
                self.port = options["gateway_service"]["port"]
        else:
            self.hostname = Constants.HOST_NAME
            self.protocol = "https"
            self.port = None

        LogManager.get_instance().debug(
            debug_messages.get("SERVICE_INITIALIZED").format(service="Settings Manager")
        )
        SettingsManager._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    def get_account_id(self):
        return self.account_id

    def get_sdk_key(self):
        return self.sdk_key

    def fetch_settings_and_cache_in_storage(self, update=False):
        try:
            settings = self.fetch_settings()
            # Simulate storing settings in a cache (memory, file, etc.)
            # For demonstration, we'll skip actual caching
            return settings
        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("SETTINGS_FETCH_ERROR").format(err=str(err))
            )
            return None


    def get_settings_path(self) -> Dict[str, Any]:
        path = {
            "i": self.sdk_key,  # Inject API key
            "r": random.random(),  # Random number for cache busting
            "a": self.account_id,  # Account ID
        }
        return path

    def fetch_settings(self, is_via_webhook=False):
        if not self.sdk_key or not self.account_id:
            raise ValueError(
                "sdk_key is required for fetching account settings. Aborting!"
            )

        network_instance = NetworkManager.get_instance()
        options = self.get_settings_path()
        options["platform"] = "server"
        options["api-version"] = 1
        options["sn"] = Constants.SDK_NAME
        options["sv"] = Constants.SDK_VERSION

        if not network_instance.get_config().get_development_mode():
            options["s"] = "prod"

        endpoint = (
            Constants.SETTINGS_ENDPOINT
            if not is_via_webhook
            else Constants.WEBHOOK_SETTINTS_ENDPOINT
        )
        # Start timer for settings fetch
        settings_fetch_start_time = time.time() * 1000  # Convert to milliseconds

        try:
            request = RequestModel(
                self.hostname,
                "GET",
                endpoint,
                options,
                None,
                None,
                self.protocol,
                self.port,
            )
            request.set_timeout(self.network_timeout)
            response = network_instance.get(request)
            response_data = response.get_data()

            if response.status_code != 200:
                raise Exception(f"Failed to fetch settings: {response_data}")

            # Calculate settings fetch time
            self.settings_fetch_time = int((time.time() * 1000) - settings_fetch_start_time)
            return response_data

        except Exception as err:
            raise err

    def get_settings(self, force_fetch=False):
        if force_fetch:
            return self.fetch_settings_and_cache_in_storage()
        else:
            # Simulate fetching settings from a cache
            # For demonstration, we'll skip actual caching
            fetched_settings = self.fetch_settings_and_cache_in_storage()
            if self.is_settings_valid(fetched_settings):
                self.is_settings_valid_on_init = True
                LogManager.get_instance().info(
                    info_messages.get("SETTINGS_FETCH_SUCCESS").format()
                )
                return fetched_settings
            else:
                LogManager.get_instance().info(
                    error_messages.get("SETTINGS_SCHEMA_INVALID")
                )
                return {}

    @staticmethod
    def is_settings_valid(settings):
        try:
            # Attempt to load the settings as JSON if it's in string format
            if isinstance(settings, str):
                settings_file = json.loads(settings)
            else:
                settings_file = settings
        except json.JSONDecodeError:
            return False

        # Validate the loaded JSON data against the schema
        validator = jsonschema.Draft7Validator(SETTINGS_FILE_SCHEMA)
        errors = sorted(validator.iter_errors(settings_file), key=lambda e: e.path)

        if errors:
            for error in errors:
                error_path = " -> ".join([str(p) for p in error.path])
                # print(f"Error at {error_path}: {error.message}")
            return False
        else:
            # print("Validation succeeded")
            return True
