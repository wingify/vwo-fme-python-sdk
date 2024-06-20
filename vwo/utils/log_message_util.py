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


import re
import json
import os
from typing import Dict, Any

# Determine the base directory (the directory containing this script)
base_dir = os.path.dirname(__file__)

def load_json_file(filename: str) -> Dict[str, str]:
    """
    Loads a JSON file and returns its content as a dictionary.
    
    :param filename: The name of the JSON file to load.
    :return: A dictionary with the contents of the JSON file.
    """
    filepath = os.path.join(base_dir, '../resources', filename)
    with open(filepath, 'r') as file:
        return json.load(file)
    
# Load all required JSON files
debug_messages = load_json_file('debug-messages.json')
error_messages = load_json_file('error-messages.json')
info_messages = load_json_file('info-message.json')
trace_messages = load_json_file('trace-messages.json')
warn_messages = load_json_file('warn-messages.json')