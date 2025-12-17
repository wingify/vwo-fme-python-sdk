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

from typing import Dict

class AliasSetResponse:
    """
    AliasSetResponse model for setting and getting the alias set response.
    """
    def __init__(self, alias_set_response_data: Dict):
        """
        Initialize the AliasSetResponse model with the provided data dictionary.

        :param alias_set_response_data: A dictionary containing the alias set response.
        """
        self.is_alias_set = alias_set_response_data.get("isAliasSet", False)

    def get_is_alias_set(self) -> bool:
        """
        Get the alias set response boolean.

        :return: The alias set response boolean.
        """
        return self.is_alias_set
        
    def set_is_alias_set(self, is_alias_set: bool) -> None:
        """
        Set the alias set response.

        :param is_alias_set: The new alias set response boolean.
        """
        self.is_alias_set = is_alias_set