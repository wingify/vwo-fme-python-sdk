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


from enum import Enum, auto


class SegmentOperandRegexEnum(Enum):
    LOWER = r"^lower"
    LOWER_MATCH = r"^lower\((.*)\)"
    WILDCARD = r"^wildcard"
    WILDCARD_MATCH = r"^wildcard\((.*)\)"
    REGEX = r"^regex"
    REGEX_MATCH = r"^regex\((.*)\)"
    STARTING_STAR = r"^\*"
    ENDING_STAR = r"\*$"
    GREATER_THAN_MATCH = r"^gt\((\d+\.?\d*|\.\d+)\)$"
    GREATER_THAN_EQUAL_TO_MATCH = r"^gte\((\d+\.?\d*|\.\d+)\)$"
    LESS_THAN_MATCH = r"^lt\((\d+\.?\d*|\.\d+)\)$"
    LESS_THAN_EQUAL_TO_MATCH = r"^lte\((\d+\.?\d*|\.\d+)\)$"
