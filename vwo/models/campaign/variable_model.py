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





from typing import Any, Dict

class VariableModel:
    def __init__(self, id: int, value: Any, type: str, key: str):
        self._id = id
        self._value = value
        self._type = type
        self._key = key

    def get_id(self) -> int:
        return self._id

    def get_value(self) -> Any:
        return self._value

    def get_type(self) -> str:
        return self._type

    def get_key(self) -> str:
        return self._key
    
    def to_dict(self) -> Dict:
        return {
            'id': self._id,
            'value': self._value,
            'type': self._type,
            'key': self._key
        }