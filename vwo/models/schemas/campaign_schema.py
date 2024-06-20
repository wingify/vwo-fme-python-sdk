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

from .campaign_variation_schema import CAMPAIGN_VARIATION_SCHEMA
from .empty_object_schema import EMPTY_OBJECT

CAMPAIGN_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": ["number", "string"]},
        "type": {"type": "string"},
        "key": {"type": "string"},
        "percentTraffic": {"type": "number"},
        "status": {"type": "string"},
        "variations": {
            "if": {"type": "array"},
            "then": {"items": CAMPAIGN_VARIATION_SCHEMA},
            "else": EMPTY_OBJECT,
        },
        "segments": {"type": "object"},
        "isForcedVariationEnabled": {"type": "boolean"},
        "isAlwaysCheckSegment": {"type": "boolean"},
        "name": {"type": "string"},
    },
    "required": ["id", "type", "key", "status", "variations", "segments", "name"],
}
