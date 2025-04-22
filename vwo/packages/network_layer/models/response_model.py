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


class ResponseModel:
    def __init__(self):
        self.status_code = None
        self.headers = {}
        self.data = None
        self.error = None

    def set_status_code(self, status_code: int):
        self.status_code = status_code

    def get_status_code(self) -> Optional[int]:
        return self.status_code

    def set_headers(self, headers: Dict[str, str]):
        self.headers = headers

    def get_headers(self) -> Dict[str, str]:
        return self.headers

    def set_data(self, data: Any):
        self.data = data

    def get_data(self) -> Any:
        return self.data

    def set_error(self, error: Any):
        self.error = error

    def get_error(self) -> Any:
        return self.error
