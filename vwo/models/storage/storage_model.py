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


from typing import Dict


class Storage:
    def __init__(self, data: Dict):
        """
        Initialize the Storage model with the provided data dictionary.

        :param data: A dictionary containing the storage attributes.
        """
        self._feature_key = data.get("featureKey", None)
        self._user = data.get("user", None)
        self._rollout_id = data.get("rolloutId", None)
        self._rollout_key = data.get("rolloutKey", None)
        self._rollout_variation_id = data.get("rolloutVariationId", None)
        self._experiment_id = data.get("experimentId", None)
        self._experiment_key = data.get("experimentKey", None)
        self._experiment_variation_id = data.get("experimentVariationId", None)

    # Getter methods for accessing private attributes
    def get_feature_key(self) -> str:
        return self._feature_key

    def get_user(self) -> str:
        return self._user

    def get_rollout_id(self) -> int:
        return self._rollout_id

    def get_rollout_key(self) -> str:
        return self._rollout_key

    def get_rollout_variation_id(self) -> int:
        return self._rollout_variation_id

    def get_experiment_id(self) -> int:
        return self._experiment_id

    def get_experiment_key(self) -> str:
        return self._experiment_key

    def get_experiment_variation_id(self) -> int:
        return self._experiment_variation_id

    # Setter methods for modifying private attributes
    def set_feature_key(self, value: str):
        self._feature_key = value

    def set_user(self, value: str):
        self._user = value

    def set_rollout_id(self, value: int):
        self._rollout_id = value

    def set_rollout_key(self, value: str):
        self._rollout_key = value

    def set_rollout_variation_id(self, value: int):
        self._rollout_variation_id = value

    def set_experiment_id(self, value: int):
        self._experiment_id = value

    def set_experiment_key(self, value: str):
        self._experiment_key = value

    def set_experiment_variation_id(self, value: int):
        self._experiment_variation_id = value
