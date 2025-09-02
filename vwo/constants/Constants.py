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


class Constants:
    # TODO: read from setup.py
    sdk_meta = {
        "name": "vwo-fme-python-sdk",
        "version": "1.12.0"
    }

    # Constants
    SDK_NAME = sdk_meta["name"]
    SDK_VERSION = sdk_meta["version"]

    PLATFORM = "server"

    MAX_TRAFFIC_PERCENT = 100
    MAX_TRAFFIC_VALUE = 10000
    STATUS_RUNNING = "RUNNING"

    SEED_VALUE = 1
    MAX_EVENTS_PER_REQUEST = 5000
    DEFAULT_REQUEST_TIME_INTERVAL = 600  # 10 * 60(secs) = 600 secs i.e. 10 minutes
    DEFAULT_EVENTS_PER_REQUEST = 100

    AP = "server"

    SEED_URL = "https://example.com/seed"  # Replace with actual URL or value
    HTTP_PROTOCOL = "http"
    HTTPS_PROTOCOL = "https"

    SETTINGS = "settings"
    SETTINGS_EXPIRY = 10000000
    SETTINGS_TIMEOUT = 50000
    POLLING_INTERVAL = 600000

    HOST_NAME = "dev.visualwebsiteoptimizer.com"  # TODO: change as needed
    SETTINGS_ENDPOINT = "/server-side/v2-settings"
    WEBHOOK_SETTINTS_ENDPOINT = "/server-side/v2-pull"
    LOCATION_ENDPOINT = "/getLocation"

    VWO_FS_ENVIRONMENT = "vwo_fs_environment"

    RANDOM_ALGO = 1

    VWO_META_MEG_KEY = "_vwo_meta_meg_"

    THREAD_POOL_MAX_WORKERS = 5
    SHOULD_USE_THREADING = True

    MAX_RETRIES = 3
    INITIAL_WAIT_TIME = 2
    PRODUCT_NAME = "fme"
