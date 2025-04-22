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

from .campaign_metric_schema import CAMPAIGN_METRIC_SCHEMA
from .rule_schema import RULE_SCHEMA
from .variable_schema import VARIABLE_SCHEMA
from .empty_object_schema import EMPTY_OBJECT

FEATURE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": ["number", "string"]},
        "key": {"type": "string"},
        "status": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "metrics": {"type": "array", "items": CAMPAIGN_METRIC_SCHEMA},
        "impactCampaign": {"type": "object"},
        "rules": {"type": "array", "items": RULE_SCHEMA},
        "variables": {
            "if": {"type": "array"},
            "then": {"items": VARIABLE_SCHEMA},
            "else": EMPTY_OBJECT,
        },
    },
    "required": ["id", "key", "status", "name", "type", "metrics"],
}
