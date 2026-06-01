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

class Alias:
    """
    Alias model for setting and getting the alias ID and user ID.
    """
    def __init__(self, alias_data: Dict):
        """
        Initialize the Alias model with the provided data dictionary.

        :param alias_data: A dictionary containing the alias ID and user ID.
        """
        self.alias = alias_data.get("aliasId", None)
        self.user_id = alias_data.get("userId", None)

    def get_alias(self) -> str:
        """
        Get the alias ID.

        :return: The alias ID as a string.
        """
        return self.alias

    def set_alias(self, alias: str) -> None:
        """
        Set the alias ID.

        :param alias: The new alias ID as a string.
        """
        self.alias = alias

    def get_user_id(self) -> str:
        """
        Get the user ID.

        :return: The user ID as a string.
        """
        return self.user_id

    def set_user_id(self, user_id: str) -> None:
        """
        Set the user ID.

        :param user_id: The new user ID as a string.
        """
        self.user_id = user_id
