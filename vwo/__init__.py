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

"""
Legacy VWO FME SDK — public package entry point.

Install via: pip install vwo-fme-python-sdk
All behavior delegates to the Wingify core; types are legacy aliases.
"""

from vwo.vwo import init, getUUID, VWOClient, VWOBuilder
from vwo.models.vwo_options_model import VWOOptionsModel
from vwo.packages.storage.connector import StorageConnector
from vwo.packages.logger.enums.log_level_enum import LogLevelEnum

__all__ = [
    "init",
    "getUUID",
    "VWOClient",
    "VWOBuilder",
    "VWOOptionsModel",
    "StorageConnector",
    "LogLevelEnum",
]
