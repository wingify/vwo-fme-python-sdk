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


import re
from ....utils.data_type_util import is_object
from typing import List


def get_key_value(obj):
    if not is_object(obj):
        return None
    key = list(obj.keys())[0]
    value = obj[key]
    return key, value


def match_with_regex(string, regex):
    try:
        return re.findall(regex, string)
    except re.error:
        return None
