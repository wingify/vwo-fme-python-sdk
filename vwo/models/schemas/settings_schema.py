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

from .empty_object_schema import EMPTY_OBJECT
from .campaign_group_schema import CAMPAIGN_GROUP_SCHEMA
from .campaign_schema import CAMPAIGN_SCHEMA
from .feature_schema import FEATURE_SCHEMA
from .group_schema import GROUP_SCHEMA

SETTINGS_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": ["number", "string"]},
        "accountId": {"type": ["number", "string"]},
        "campaigns": {
            "if": {"type": "array"},
            "then": {"items": CAMPAIGN_SCHEMA},
            "else": EMPTY_OBJECT,
        },
        "features": {
            "if": {"type": "array"},
            "then": {"items": FEATURE_SCHEMA},
            "else": EMPTY_OBJECT,
        },
        "campaignGroups": CAMPAIGN_GROUP_SCHEMA,
        "groups": GROUP_SCHEMA,
    },
    "required": ["version", "accountId", "campaigns", "features"],
}
