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

from .variable_schema import VARIABLE_SCHEMA
from .empty_object_schema import EMPTY_OBJECT

CAMPAIGN_VARIATION_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": ["number", "string"]},
        "name": {"type": "string"},
        "weight": {"type": ["number", "string"]},
        "segments": {"type": "object"},
        "variables": {
            "if": {"type": "array"},
            "then": {"items": VARIABLE_SCHEMA},
            "else": EMPTY_OBJECT,
        },
        "startRangeVariation": {"type": "number"},
        "endRangeVariation": {"type": "number"},
    },
    "required": ["id", "name", "weight"],
}
