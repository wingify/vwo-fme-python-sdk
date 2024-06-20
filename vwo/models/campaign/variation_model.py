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




from typing import List, Dict, Any
from .variable_model import VariableModel

class VariationModel:
    def __init__(self, id: int, segments: Dict[str, Any], weight: float, name: str, variables: List[VariableModel],
                 start_range_variation: float, end_range_variation: float, variations: List['VariationModel'] = []):
        self._id = id
        self._segments = segments
        self._weight = weight
        self._name = name
        self._variables = variables
        self._start_range_variation = start_range_variation
        self._end_range_variation = end_range_variation
        self._variations = variations

    def get_id(self) -> int:
        return self._id

    def get_segments(self) -> Dict[str, Any]:
        return self._segments

    def get_weight(self) -> float:
        return self._weight

    def get_name(self) -> str:
        return self._name

    def get_variables(self) -> List[VariableModel]:
        return self._variables
    
    def get_start_range_variation(self) -> float:
        return self._start_range_variation
    
    def get_end_range_variation(self) -> float:
        return self._end_range_variation
    
    def get_variations(self) -> List['VariationModel']:
        return self._variations
    
    def set_variations(self, variations: List['VariationModel']) -> None:
        self._variations = variations
    
    def set_start_range_variation(self, start_range_variation: float) -> None:
        self._start_range_variation = start_range_variation

    def set_end_range_variation(self, end_range_variation: float) -> None:
        self._end_range_variation = end_range_variation

    def set_weight(self, weight: float) -> None:
        self._weight = weight