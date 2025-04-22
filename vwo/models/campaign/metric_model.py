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


class MetricModel:
    def __init__(
        self,
        id: int,
        hasProps: Optional[bool] = False,
        type: str = None,
        identifier: str = None,
    ):
        self._id = id
        self._has_props = hasProps
        self._type = type
        self._identifier = identifier

    def get_id(self) -> int:
        return self._id

    def get_has_props(self) -> bool:
        return self._has_props

    def get_type(self) -> str:
        return self._type

    def get_identifier(self) -> str:
        return self._identifier
