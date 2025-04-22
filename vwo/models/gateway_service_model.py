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


from typing import Dict


class gateway_serviceModel:
    def __init__(self, gateway_service: Dict):
        """
        Initialize the gateway_serviceModel with a URL and a port number.

        :param gateway_service: A dictionary containing the URL and port of the gateway service.
        """
        self.url = gateway_service.get(
            "url", ""
        )  # Default to an empty string if url is missing
        # Use get with a default value to handle missing or null 'port'
        self.port = gateway_service.get(
            "port", None
        )  # Default to None if port is missing

    def get_url(self) -> str:
        """
        Get the URL of the gateway service.

        :return: The URL as a string.
        """
        return self.url

    def get_port(self) -> int:
        """
        Get the port number of the gateway service.

        :return: The port number as an integer.
        """
        return self.port
