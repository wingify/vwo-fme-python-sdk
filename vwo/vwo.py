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


from typing import Dict, Any, Optional
from vwo.vwo_builder import VWOBuilder
from vwo.vwo_client import VWOClient
from vwo.enums.url_enum import UrlEnum


class VWO:
    vwo_builder: "VWOBuilder" = None
    instance: "VWOClient" = None

    def __init__(self, options: Dict):
        VWO.set_instance(options)

    @staticmethod
    def set_instance(options: Dict) -> "VWOClient":
        options_vwo_builder = options.get("vwoBuilder", None)
        VWO.vwo_builder = options_vwo_builder or VWOBuilder(options)

        # Configure the builder
        VWO.vwo_builder.set_logger().set_settings_manager().set_storage().set_network_manager().set_segmentation().init_polling().init_usage_stats()

        # Fetch settings synchronously and build the VWO instance
        settings = VWO.vwo_builder.get_settings(force=False)
        VWO.instance = VWO.vwo_builder.build(settings)
        
        # Initialize batching
        VWO.vwo_builder.init_batching()
        return VWO.instance

    @staticmethod
    def getInstance() -> Optional["VWO"]:
        return VWO.instance


def init(options: Dict[str, Any]) -> Optional["VWOClient"]:
    if not options or "sdk_key" not in options or not options["sdk_key"]:
        print(
            "SDK key is required to initialize VWO. Please provide the sdk_key in the options.",
            None,
        )
        return None

    if not options or "account_id" not in options or not options["account_id"]:
        print(
            "Account ID is required to initialize VWO. Please provide the account_id in the options.",
            None,
        )
        return None

    instance = VWO.set_instance(options)
    return instance
