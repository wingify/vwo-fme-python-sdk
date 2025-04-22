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


from typing import Optional


class RuleModel:
    def __init__(
        self,
        type: str,
        ruleKey: Optional[str],
        variationId: Optional[int] = None,
        campaignId: int = None,
    ):
        self._type = type
        self._rule_key = ruleKey
        self._variation_id = variationId
        self._campaign_id = campaignId

    def get_type(self) -> str:
        return self._type

    def get_rule_key(self) -> Optional[str]:
        return self._rule_key

    def get_variation_id(self) -> Optional[int]:
        return self._variation_id

    def get_campaign_id(self) -> int:
        return self._campaign_id
