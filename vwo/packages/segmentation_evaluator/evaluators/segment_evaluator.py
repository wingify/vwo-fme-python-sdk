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


from ..utils.segment_util import get_key_value
from ..enums.segment_operator_value_enum import SegmentOperatorValueEnum
from ..evaluators.segment_operand_evaluator import SegmentOperandEvaluator
from ....models.user.context_model import ContextModel
from ....models.settings.settings_model import SettingsModel
from ....models.campaign.feature_model import FeatureModel
from ...logger.core.log_manager import LogManager
from ....services.storage_service import StorageService
from ....decorators.storage_decorator import StorageDecorator
import re
from typing import Dict, List, Any


class SegmentEvaluator:
    def __init__(self):
        self.context: ContextModel = None
        self.settings: SettingsModel = None
        self.feature: FeatureModel = None

    def is_segmentation_valid(self, dsl, properties):
        key, value = get_key_value(dsl)
        operator = key
        sub_dsl = value

        # Evaluate based on the type of segmentation operator
        if operator == SegmentOperatorValueEnum.NOT.value:
            result = self.is_segmentation_valid(sub_dsl, properties)
            return not result
        elif operator == SegmentOperatorValueEnum.AND.value:
            return self.every(sub_dsl, properties)
        elif operator == SegmentOperatorValueEnum.OR.value:
            return self.some(sub_dsl, properties)
        elif operator == SegmentOperatorValueEnum.CUSTOM_VARIABLE.value:
            return SegmentOperandEvaluator().evaluate_custom_variable_dsl(
                sub_dsl, properties
            )
        elif operator == SegmentOperatorValueEnum.USER.value:
            return SegmentOperandEvaluator().evaluate_user_dsl(sub_dsl, properties)
        elif operator == SegmentOperatorValueEnum.UA.value:
            return SegmentOperandEvaluator().evaluate_user_agent_dsl(
                sub_dsl, self.context
            )
        else:
            return False

    def some(self, dsl_nodes, custom_variables: Dict[str, Any]):
        ua_parser_map: Dict[str, List[str]] = {}
        key_count = 0
        is_ua_parser = False

        for dsl in dsl_nodes:
            for key in dsl:
                if key in [
                    SegmentOperatorValueEnum.OPERATING_SYSTEM.value,
                    SegmentOperatorValueEnum.BROWSER_AGENT.value,
                    SegmentOperatorValueEnum.DEVICE_TYPE.value,
                    SegmentOperatorValueEnum.DEVICE.value,
                ]:
                    is_ua_parser = True
                    value = dsl[key]

                    if key not in ua_parser_map:
                        ua_parser_map[key] = []

                    values_array = value if isinstance(value, List) else [value]
                    for val in values_array:
                        if isinstance(val, str):
                            ua_parser_map[key].append(val)

                    key_count += 1

                if key == SegmentOperatorValueEnum.FEATURE_ID.value:
                    feature_id_object = dsl[key]
                    feature_id_key = list(feature_id_object.keys())[0]
                    feature_id_value = feature_id_object[feature_id_key]
                    if feature_id_value == "on" or feature_id_value == "off":
                        features = self.settings.get_features()
                        feature = next(
                            (f for f in features if f.get_id() == int(feature_id_key)),
                            None,
                        )

                        if feature:
                            feature_key = feature.get_key()
                            result = self.check_in_user_storage(
                                self.settings, feature_key, self.context
                            )
                            if feature_id_value == "off":
                                return not result
                            return result
                        else:
                            LogManager.get_instance().error(
                                f"Feature not found with featureIdKey: {feature_id_key}"
                            )
                            return None

            if is_ua_parser and key_count == len(dsl_nodes):
                try:
                    ua_parser_result = self.check_user_agent_parser(ua_parser_map)
                    return ua_parser_result
                except Exception as err:
                    LogManager.get_instance().error(
                        f"Failed to validate User Agent. Error: {err}"
                    )

            if self.is_segmentation_valid(dsl, custom_variables):
                return True

        return False

    def every(self, dsl_nodes, custom_variables: Dict[str, Any]):
        location_map = {}
        for dsl in dsl_nodes:
            if any(
                key in dsl
                for key in [
                    SegmentOperatorValueEnum.COUNTRY.value,
                    SegmentOperatorValueEnum.REGION.value,
                    SegmentOperatorValueEnum.CITY.value,
                ]
            ):
                self.add_location_values_to_map(dsl, location_map)
                if len(location_map) == len(dsl_nodes):
                    segment_result = self.check_location_pre_segmentation(location_map)
                    return segment_result
                continue
            res = self.is_segmentation_valid(dsl, custom_variables)
            if not res:
                return False
        return True

    def add_location_values_to_map(self, dsl, location_map: Dict[str, Any]):
        if SegmentOperatorValueEnum.COUNTRY.value in dsl:
            location_map[SegmentOperatorValueEnum.COUNTRY.value] = dsl[
                SegmentOperatorValueEnum.COUNTRY.value
            ]
        if SegmentOperatorValueEnum.REGION.value in dsl:
            location_map[SegmentOperatorValueEnum.REGION.value] = dsl[
                SegmentOperatorValueEnum.REGION.value
            ]
        if SegmentOperatorValueEnum.CITY.value in dsl:
            location_map[SegmentOperatorValueEnum.CITY.value] = dsl[
                SegmentOperatorValueEnum.CITY.value
            ]

    def check_location_pre_segmentation(self, location_map: Dict[str, Any]):
        if self.context.get_ip_address() is None:
            LogManager.get_instance().info(
                "To evaluate location pre Segment, please pass ip_address in context object"
            )
            return False
        if not self.context.get_vwo() or self.context.get_vwo().get_location() is None:
            return False
        return self.values_match(location_map, self.context.get_vwo().get_location())

    def check_user_agent_parser(self, ua_parser_map: Dict[str, List[str]]):
        if not self.context.get_user_agent():
            LogManager.get_instance().info(
                "To evaluate user agent related segments, please pass user_agent in context object"
            )
            return False
        if not self.context.get_vwo() or self.context.get_vwo().get_ua_info() is None:
            return False
        return self.check_value_present(
            ua_parser_map, self.context.get_vwo().get_ua_info()
        )

    def check_in_user_storage(self, settings, feature_key, context):
        storage_service = StorageService()
        stored_data = StorageDecorator().get_feature_from_storage(
            feature_key, context, storage_service
        )
        if stored_data and len(stored_data) > 0:
            return True
        else:
            return False

    def check_value_present(
        self, expected_map: Dict[str, List[str]], actual_map: Dict[str, str]
    ):
        for key, actual_value in actual_map.items():
            if key in expected_map:
                expected_values = expected_map[key]
                expected_values = [val.lower() for val in expected_values]
                for val in expected_values:
                    if val.startswith("wildcard(") and val.endswith(")"):
                        wildcard_pattern = val[9:-1]
                        regex = re.compile(
                            wildcard_pattern.replace("*", ".*"), re.IGNORECASE
                        )
                        if regex.match(actual_value):
                            return True
                if actual_value.lower() in expected_values:
                    return True
        return False

    def values_match(
        self, expected_location_map: Dict[str, Any], user_location: Dict[str, str]
    ):
        for key, value in expected_location_map.items():
            if key in user_location:
                normalized_value1 = self.normalize_value(value)
                normalized_value2 = self.normalize_value(user_location[key])
                if normalized_value1 != normalized_value2:
                    return False
            else:
                return False
        return True

    def normalize_value(self, value):
        if value is None:
            return None
        return str(value).replace('"', "").strip()
