# Copyright 2024-2026 Wingify Software Pvt. Ltd.
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

from typing import Any, Dict, List

from .metric_model import MetricModel


class HoldoutModel:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize the HoldoutModel with the provided data dictionary.

        :param data: A dictionary containing holdout configuration.
        """
        data = data or {}

        self._id = data.get("id")
        self._segments = data.get("segments") or {}
        self._percent_traffic = data.get("percentTraffic", 0)
        self._is_global = bool(data.get("isGlobal", False))

        feature_ids = data.get("featureIds", [])
        self._feature_ids = feature_ids if isinstance(feature_ids, list) else []

        self._name = data.get("name", "")

        # Gateway service requirement flag
        self._is_gateway_service_required = bool(
            data.get("isGatewayServiceRequired", False)
        )

        # Metrics list: supports both "m" and "metrics" keys, mirroring the TS model.
        raw_metrics = data.get("m") or data.get("metrics") or []
        if isinstance(raw_metrics, dict):
            metrics_list: List[MetricModel] = []
        else:
            metrics_list = []
            for metric_data in raw_metrics or []:
                if not isinstance(metric_data, dict):
                    continue
                # Keep construction consistent with MetricModel usage in model_utils._parse_metric
                metrics_list.append(
                    MetricModel(
                        id=metric_data.get("id"),
                        hasProps=metric_data.get("hasProps", None),
                        type=metric_data.get("type"),
                        identifier=metric_data.get("identifier"),
                    )
                )

        self._metrics = metrics_list

    def get_id(self) -> int:
        return self._id

    def get_segments(self) -> Dict[str, Any]:
        return self._segments or {}

    def get_percent_traffic(self) -> int:
        return self._percent_traffic

    def get_is_global(self) -> bool:
        return self._is_global

    def get_feature_ids(self) -> List[int]:
        return self._feature_ids

    def get_metrics(self) -> List[MetricModel]:
        return self._metrics

    def get_is_gateway_service_required(self) -> bool:
        return self._is_gateway_service_required

    def set_is_gateway_service_required(self, is_gateway_service_required: bool) -> None:
        self._is_gateway_service_required = is_gateway_service_required

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

