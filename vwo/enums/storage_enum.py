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


from enum import Enum


class StorageEnum(Enum):
    STORAGE_UNDEFINED = "Storage is undefined"
    INCORRECT_DATA = "Incorrect data"
    NO_DATA_FOUND = "No data found"
    CAMPAIGN_PAUSED = "Campaign paused"
    VARIATION_NOT_FOUND = "Variation not found"
    WHITELISTED_VARIATION = "Whitelisted variation"
