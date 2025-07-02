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


class RequestModel:
    def __init__(
        self,
        url: Optional[str] = None,
        method: str = "GET",
        path: str = "",
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        scheme: str = "https",
        port: Optional[int] = None,
        timeout: int = 3000,
    ):
        self.url = url
        self.method = method
        self.path = path
        self.query = query or {}
        self.body = body or {}
        self.headers = headers or {}
        self.scheme = scheme
        self.port = port
        self.timeout = timeout / 1000  # Convert milliseconds to seconds

    def get_method(self) -> str:
        return self.method

    def set_method(self, method: str):
        self.method = method

    def get_body(self) -> Dict[str, Any]:
        return self.body

    def set_body(self, body: Dict[str, Any]):
        self.body = body

    def set_query(self, query: Dict[str, Any]):
        self.query = query

    def get_query(self) -> Dict[str, Any]:
        return self.query

    def set_headers(self, headers: Dict[str, str]):
        self.headers = headers

    def get_headers(self) -> Dict[str, str]:
        return self.headers

    def set_timeout(self, timeout: int):
        self.timeout = timeout / 1000

    def get_timeout(self) -> int:
        return int(self.timeout * 1000)

    def get_url(self) -> Optional[str]:
        return self.url

    def set_url(self, url: str):
        self.url = url

    def get_scheme(self) -> str:
        return self.scheme

    def set_scheme(self, scheme: str):
        self.scheme = scheme

    def get_port(self) -> Optional[int]:
        return self.port

    def set_port(self, port: int):
        self.port = port

    def get_path(self) -> str:
        return self.path

    def set_path(self, path: str):
        self.path = path

    def set_user_id(self, user_id: str):
        self.user_id = user_id

    def get_user_id(self) -> str:
        return self.user_id

    def get_options(self) -> Dict[str, Any]:
        query_params = "&".join([f"{key}={value}" for key, value in self.query.items()])
        options = {
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "timeout": self.timeout,
        }

        if self.scheme and self.url:
            options["url"] = f"{self.scheme}://{self.url}"

        if self.port:
            options["url"] += f":{self.port}"

        if self.path:
            options["url"] += self.path

        if query_params:
            options["url"] += f"?{query_params}"

        if self.body:
            options["json"] = self.body

        return options
