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

import os
import json
from typing import Dict

# Determine the base directory (the directory containing this script)
base_dir = os.path.dirname(__file__)

def load_settings_json_files(directory_path):
    """
    Load all JSON files from a specified directory into a dictionary.

    :param directory_path: Path to the directory containing JSON files.
    :return: Dictionary where keys are filenames and values are JSON contents.
    """
    json_files_content = {}

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_content = json.load(file)
                    # remove .json from filename
                    filename = filename.split('.')[0]
                    json_files_content[filename] = json_content
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {filename}: {e}")

    return json_files_content

def load_test_data_json_file(filename: str) -> Dict[str, str]:
    """
    Loads a JSON file and returns its content as a dictionary.
    
    :param filename: The name of the JSON file to load.
    :return: A dictionary with the contents of the JSON file.
    """
    filepath = os.path.join(base_dir, 'test_cases', filename)
    with open(filepath, 'r') as file:
        return json.load(file)


# Load the JSON files
settings_files = load_settings_json_files(os.path.join(base_dir, 'settings'))
test_data = load_test_data_json_file('index.json')
segmentor_dummy_dsl = load_test_data_json_file('dummy_dsl.json')