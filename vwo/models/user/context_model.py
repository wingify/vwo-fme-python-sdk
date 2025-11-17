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


from .context_vwo_model import ContextVWOModel
from typing import Dict, List
from ...utils.uuid_util import get_uuid
from ...services.settings_manager import SettingsManager
from ...utils.function_util import get_current_unix_timestamp

class ContextModel:
    def __init__(self, context: Dict):
        self.id = context.get("id")
        self.user_agent = context.get("user_agent", None)
        self.ip_address = context.get("ip_address", None)
        self.custom_variables = context.get("custom_variables", {})
        self.variation_targeting_variables = context.get(
            "variation_targeting_variables", {}
        )
        self._vwo = ContextVWOModel(context.get("_vwo")) if "_vwo" in context else None
        self.post_segmentation_variables = context.get("post_segmentation_variables", [])
        self._vwo_uuid = get_uuid(self.id, str(SettingsManager.get_instance().get_account_id()))
        self._vwo_session_id = get_current_unix_timestamp()

    def get_id(self) -> str:
        return str(self.id) if self.id is not None else None

    def get_user_agent(self) -> str:
        return self.user_agent

    def get_ip_address(self) -> str:
        return self.ip_address

    def get_custom_variables(self) -> Dict:
        return self.custom_variables

    def set_custom_variables(self, custom_variables: Dict) -> None:
        self.custom_variables = custom_variables

    def get_variation_targeting_variables(self) -> Dict:
        return self.variation_targeting_variables

    def set_variation_targeting_variables(
        self, variation_targeting_variables: Dict
    ) -> None:
        self.variation_targeting_variables = variation_targeting_variables

    def get_vwo(self) -> ContextVWOModel:
        return self._vwo

    def set_vwo(self, vwo: ContextVWOModel) -> None:
        self._vwo = vwo

    def get_post_segmentation_variables(self) -> List[str]:
        return self.post_segmentation_variables

    def set_post_segmentation_variables(self, post_segmentation_variables: List[str]) -> None:
        self.post_segmentation_variables = post_segmentation_variables

    def get_vwo_uuid(self) -> str:
        return self._vwo_uuid

    def get_vwo_session_id(self) -> str:
        return self._vwo_session_id

    def set_vwo_uuid(self, vwo_uuid: str) -> None:
        self._vwo_uuid = vwo_uuid

    def set_vwo_session_id(self, vwo_session_id: str) -> None:
        self._vwo_session_id = vwo_session_id