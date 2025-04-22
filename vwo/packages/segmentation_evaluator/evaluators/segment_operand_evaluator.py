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
from typing import Dict, Any
from ..utils.segment_util import get_key_value, match_with_regex
from ..enums.segment_operand_regex_enum import SegmentOperandRegexEnum
from ..enums.segment_operand_value_enum import SegmentOperandValueEnum
from ...logger.core.log_manager import LogManager
from ....utils.gateway_service_util import get_from_gateway_service
from ....enums.url_enum import UrlEnum
from ....utils.data_type_util import is_boolean
from ....models.user.context_model import ContextModel
from ....services.settings_manager import SettingsManager


class SegmentOperandEvaluator:
    def evaluate_custom_variable_dsl(
        self, dsl_operand_value, properties: Dict[str, Any]
    ):
        """
        Evaluates a custom variable DSL expression.

        :param dsl_operand_value: The DSL expression for the custom variable.
        :param properties: The properties object containing the actual values to be matched against.
        :return: A boolean indicating if the DSL condition is met.
        """
        key, value = get_key_value(dsl_operand_value)
        operand_key = key
        operand = value

        if operand_key not in properties:
            return False

        if "inlist" in operand:
            list_id_regex = r"inlist\([^)]*\)"
            match = re.search(list_id_regex, operand)
            if not match or len(match.groups()) < 1:
                print("Invalid 'inList' operand format")
                return False

            tag_value = properties[operand_key]
            attribute_value = self.pre_process_tag_value(tag_value)
            list_id = match.group(1)
            query_params_obj = {
                "attribute": attribute_value,
                "listId": list_id,
                "accountId": SettingsManager.get_instance().account_id,
                "sdkKey": SettingsManager.get_instance().sdk_key,
            }

            try:
                res = get_from_gateway_service(
                    query_params_obj, UrlEnum.ATTRIBUTE_CHECK.value
                )
                if not res or res == "false":
                    return False
                return res
            except Exception as error:
                print("Error while fetching data:", error)
                return False
        else:
            tag_value = properties[operand_key]
            tag_value = self.pre_process_tag_value(tag_value)
            operand_type, operand_value = self.pre_process_operand_value(
                operand
            ).values()
            processed_values = self.process_values(operand_value, tag_value)
            tag_value = processed_values["tag_value"]
            return self.extract_result(
                operand_type, processed_values["operand_value"], tag_value
            )

    def evaluate_user_dsl(self, dsl_operand_value, properties):
        """
        Evaluates a user DSL expression to check if a user ID is in a specified List.

        :param dsl_operand_value: The DSL expression containing user IDs.
        :param properties: The properties object containing the actual user ID to check.
        :return: True if the user ID is in the List, otherwise False.
        """
        users = dsl_operand_value.split(",")
        return any(user.strip() == properties.get("_vwoUserId") for user in users)

    def evaluate_user_agent_dsl(self, dsl_operand_value, context: ContextModel):
        """
        Evaluates a user agent DSL expression.

        :param dsl_operand_value: The DSL expression for the user agent.
        :param context: The context object containing the user agent string.
        :return: True if the user agent matches the DSL condition, otherwise False.
        """
        operand = dsl_operand_value
        if not context.get_user_agent():
            LogManager.get_instance().info(
                "To Evaluate user_agent segmentation, please provide user_agent in context"
            )
            return False

        tag_value = context.get_user_agent()
        tag_value = self.pre_process_tag_value(tag_value)
        operand_type, operand_value = self.pre_process_operand_value(operand).values()
        processed_values = self.process_values(operand_value, tag_value)
        tag_value = processed_values["tag_value"]
        return self.extract_result(
            operand_type, processed_values["operand_value"], tag_value
        )

    def pre_process_tag_value(self, tag_value):
        """
        Pre-processes the tag value to ensure it is in the correct format for evaluation.

        :param tag_value: The value to be processed.
        :return: The processed tag value, either as a string or a boolean.
        """
        if tag_value is None:
            return ""

        if is_boolean(tag_value):
            return bool(tag_value)

        if tag_value is not None:
            return str(tag_value)

        return tag_value

    def pre_process_operand_value(self, operand):
        """
        Pre-processes the operand value to determine its type and extract the value based on regex matches.

        :param operand: The operand to be processed.
        :return: A dictionary containing the operand type and value.
        """
        operand_type: str = None
        operand_value: str = None

        if match_with_regex(operand, SegmentOperandRegexEnum.LOWER_MATCH.value):
            operand_type = SegmentOperandValueEnum.LOWER_VALUE.value
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.LOWER_MATCH.value
            )
        elif match_with_regex(operand, SegmentOperandRegexEnum.WILDCARD_MATCH.value):
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.WILDCARD_MATCH.value
            )
            starting_star = match_with_regex(
                operand_value, SegmentOperandRegexEnum.STARTING_STAR.value
            )
            ending_star = match_with_regex(
                operand_value, SegmentOperandRegexEnum.ENDING_STAR.value
            )

            if starting_star and ending_star:
                operand_type = SegmentOperandValueEnum.STARTING_ENDING_STAR_VALUE.value
            elif starting_star:
                operand_type = SegmentOperandValueEnum.STARTING_STAR_VALUE.value
            elif ending_star:
                operand_type = SegmentOperandValueEnum.ENDING_STAR_VALUE.value

            operand_value = operand_value.lstrip("*").rstrip("*")
        elif match_with_regex(operand, SegmentOperandRegexEnum.REGEX_MATCH.value):
            operand_type = SegmentOperandValueEnum.REGEX_VALUE.value
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.REGEX_MATCH.value
            )
        elif match_with_regex(
            operand, SegmentOperandRegexEnum.GREATER_THAN_MATCH.value
        ):
            operand_type = SegmentOperandValueEnum.GREATER_THAN_VALUE.value
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.GREATER_THAN_MATCH.value
            )
        elif match_with_regex(
            operand, SegmentOperandRegexEnum.GREATER_THAN_EQUAL_TO_MATCH.value
        ):
            operand_type = SegmentOperandValueEnum.GREATER_THAN_EQUAL_TO_VALUE.value
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.GREATER_THAN_EQUAL_TO_MATCH.value
            )
        elif match_with_regex(operand, SegmentOperandRegexEnum.LESS_THAN_MATCH.value):
            operand_type = SegmentOperandValueEnum.LESS_THAN_VALUE.value
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.LESS_THAN_MATCH.value
            )
        elif match_with_regex(
            operand, SegmentOperandRegexEnum.LESS_THAN_EQUAL_TO_MATCH.value
        ):
            operand_type = SegmentOperandValueEnum.LESS_THAN_EQUAL_TO_VALUE.value
            operand_value = self.extract_operand_value(
                operand, SegmentOperandRegexEnum.LESS_THAN_EQUAL_TO_MATCH.value
            )
        else:
            operand_type = SegmentOperandValueEnum.EQUAL_VALUE.value
            operand_value = operand

        return {"operand_type": operand_type, "operand_value": operand_value}

    def extract_operand_value(self, operand, regex):
        """
        Extracts the operand value from a string based on a specified regex pattern.

        :param operand: The operand string to extract from.
        :param regex: The regex pattern to use for extraction.
        :return: The extracted value.
        """
        match = re.search(regex, operand)
        return match.group(1) if match else None

    def process_values(self, operand_value, tag_value):
        """
        Processes numeric values from operand and tag values, converting them to strings.

        :param operand_value: The operand value to process.
        :param tag_value: The tag value to process.
        :return: A dictionary containing the processed operand and tag values as strings.
        """
        # Process both operand and tag values
        processed_operand_value = self.convert_value(operand_value)
        processed_tag_value = self.convert_value(tag_value)

        return {
            "operand_value": processed_operand_value,
            "tag_value": processed_tag_value,
        }

    def extract_result(self, operand_type: str, operand_value: str, tag_value: str):
        """
        Extracts the result of the evaluation based on the operand type and values.

        :param operand_type: The type of the operand.
        :param operand_value: The value of the operand.
        :param tag_value: The value of the tag to compare against.
        :return: The result of the evaluation.
        """
        if tag_value is None:
            return False

        # Ensure operand_value and tag_value are strings
        operand_value = str(operand_value)
        tag_value = str(tag_value)
        if operand_type == SegmentOperandValueEnum.LOWER_VALUE.value:
            return operand_value.lower() == tag_value.lower()
        elif operand_type == SegmentOperandValueEnum.STARTING_ENDING_STAR_VALUE.value:
            return operand_value in tag_value
        elif operand_type == SegmentOperandValueEnum.STARTING_STAR_VALUE.value:
            return tag_value.endswith(operand_value)
        elif operand_type == SegmentOperandValueEnum.ENDING_STAR_VALUE.value:
            return tag_value.startswith(operand_value)
        elif operand_type == SegmentOperandValueEnum.REGEX_VALUE.value:
            try:
                pattern = re.compile(operand_value)
                return bool(pattern.search(tag_value))
            except re.error:
                return False
        elif operand_type == SegmentOperandValueEnum.GREATER_THAN_VALUE.value:
            try:
                return float(tag_value) > float(operand_value)
            except ValueError:
                return False
        elif operand_type == SegmentOperandValueEnum.GREATER_THAN_EQUAL_TO_VALUE.value:
            try:
                return float(tag_value) >= float(operand_value)
            except ValueError:
                return False
        elif operand_type == SegmentOperandValueEnum.LESS_THAN_VALUE.value:
            try:
                return float(tag_value) < float(operand_value)
            except ValueError:
                return False
        elif operand_type == SegmentOperandValueEnum.LESS_THAN_EQUAL_TO_VALUE.value:
            try:
                return float(tag_value) <= float(operand_value)
            except ValueError:
                return False
        else:
            return tag_value == operand_value

    def convert_value(self, value):
        # Check if the value is a boolean
        if isinstance(value, bool):
            return str(value)  # Return "True" or "False" as a string
        try:
            numeric_value = float(value)
            # Check if the numeric value is actually an integer
            if numeric_value.is_integer():
                return str(
                    int(numeric_value)
                )  # Convert to int and then to string to remove '.0'
            else:
                return str(numeric_value)  # Keep as float and convert to string
        except ValueError:
            # Return the value as is if it's not a number
            return value
