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
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Now you can import the module
from vwo.packages.storage.connector import StorageConnector

client_db: Dict[str, Dict] = {}


class user_storage(StorageConnector):
    def get(self, key: str, user_id: str):
        return client_db.get(key + "_" + user_id)

    def set(self, value: Dict[str, Any]):
        key = value.get("featureKey") + "_" + value.get("userId")
        client_db[key] = {
            "rolloutKey": value.get("rolloutKey"),
            "rolloutVariationId": value.get("rolloutVariationId"),
            "rolloutId": value.get("rolloutId"),
            "experimentKey": value.get("experimentKey"),
            "experimentVariationId": value.get("experimentVariationId"),
            "experimentId": value.get("experimentId"),
        }
        return True

    def clear(self):
        """Clear the storage."""
        client_db.clear()
