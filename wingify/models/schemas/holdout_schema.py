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

from .campaign_metric_schema import CAMPAIGN_METRIC_SCHEMA

HOLDOUT_SCHEMA = {
    "type": "object",
    "properties": {
        "metrics": {"type": "array", "items": CAMPAIGN_METRIC_SCHEMA},
        "segments": {"type": "object"},
        "featureIds": {"type": "array", "items": {"type": "number"}},
        "isGlobal": {"type": "boolean"},
        "name": {"type": "string"},
        "id": {"type": ["number", "string"]},
        "percentTraffic": {"type": "number"},
    },
    "required": ["metrics", "segments", "featureIds", "isGlobal", "name", "id", "percentTraffic"],
}
