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


from typing import Dict, Any, Optional


class GlobalRequestModel:
    def __init__(
        self,
        url: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 3000,
        is_development_mode: bool = False,
    ):
        self.url = url
        self.query = query or {}
        self.body = body or {}
        self.headers = headers or {}
        self.timeout = timeout / 1000  # Convert milliseconds to seconds
        self.is_development_mode = is_development_mode

    def set_query(self, query: Dict[str, Any]):
        self.query = query

    def get_query(self) -> Dict[str, Any]:
        return self.query

    def set_body(self, body: Dict[str, Any]):
        self.body = body

    def get_body(self) -> Dict[str, Any]:
        return self.body

    def set_base_url(self, url: str):
        self.url = url

    def get_base_url(self) -> str:
        return self.url

    def set_timeout(self, timeout: int):
        self.timeout = timeout / 1000

    def get_timeout(self) -> int:
        return int(self.timeout * 1000)

    def set_headers(self, headers: Dict[str, str]):
        self.headers = headers

    def get_headers(self) -> Dict[str, str]:
        return self.headers

    def set_development_mode(self, is_development_mode: bool):
        self.is_development_mode = is_development_mode

    def get_development_mode(self) -> bool:
        return self.is_development_mode
