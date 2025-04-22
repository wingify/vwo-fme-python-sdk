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


from ..campaign.variable_model import VariableModel
from typing import List, Any, Dict


class GetFlag:
    def __init__(self):
        self._is_enabled = False
        self._variables = []

    def is_enabled(self) -> bool:
        return self._is_enabled

    def set_is_enabled(self, is_enabled: bool) -> None:
        self._is_enabled = is_enabled

    def get_variables(self) -> List[Dict[str, Any]]:
        # convert variables to Dict
        variables = []
        for variable in self._variables:
            variables.append(variable.to_dict())
        return variables

    def set_variables(self, variables: List[VariableModel]) -> None:
        self._variables = variables

    def get_variable(self, variable_key: str, default_value: Any = None) -> str:
        for variable in self._variables:
            if variable.get_key() == variable_key:
                return variable.get_value()
        return default_value
