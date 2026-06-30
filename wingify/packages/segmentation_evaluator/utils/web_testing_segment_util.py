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

import json
import math
import re
from typing import Any, Dict, Optional, Tuple

from ....models.user.context_model import ContextModel
from ....utils.data_type_util import (
    get_type,
    is_array,
    is_boolean,
    is_defined,
    is_null,
    is_number,
    is_object,
    is_string,
)
from ...logger.core.log_manager import LogManager
from ....enums.api_enum import ApiEnum
from ..enums.segment_operator_value_enum import SegmentOperatorValueEnum

_WEB_TESTING_JSON_STRING_KEY_REGEX = re.compile(r'"([^"\\]*)"\s*:')

def coerce_campaign_variation_operand_to_str(operand: Any) -> Optional[str]:
    """
    Coerces a campaignVariation operand to a string when the value is a valid string or finite number.

    :param operand: Raw campaignVariation operand from the segmentation DSL.
    :return: Coerced operand string, or None if the type cannot be coerced.
    """
    if is_null(operand):
        return None
    if is_boolean(operand):
        return None
    if is_string(operand):
        return operand
    if is_number(operand):
        # bool excluded above; avoids treating True as 1 via int subclassing.
        if type(operand) is float:
            if not math.isfinite(operand):
                return None
            if operand.is_integer():
                return str(int(operand))
            return str(operand)
        return str(operand)
    if is_array(operand) or is_object(operand):
        return None
    return None


def normalize_web_testing_campaigns_map(web_testing_source: Dict) -> Dict[str, str]:
    """
    Normalizes a web_testing_campaigns map so campaign and variation IDs are non-empty string keys and values.

    :param web_testing_source: Campaign ID to variation ID map from context or parsed JSON.
    :return: Map with string campaign keys and string variation values.
    """
    normalized_campaigns_map: Dict[str, str] = {}
    # iterate over the web testing source and normalize the campaign ids and variation ids
    for campaign_key in web_testing_source:
        variation_raw = web_testing_source[campaign_key]
        # convert the campaign key to a string
        campaign_key_as_str = str(campaign_key)
        # if the variation raw is not None and the campaign key as string is not empty, then add the campaign key and variation to the normalized campaigns map
        if is_defined(variation_raw) and len(campaign_key_as_str) > 0:
            normalized_campaigns_map[campaign_key_as_str] = str(variation_raw)
    return normalized_campaigns_map


def _log_first_duplicate_json_object_key_scan(
    web_testing_campaigns_json: str,
    context: ContextModel,
) -> None:
    """
    Scans a web_testing_campaigns JSON string for duplicate object keys and logs the first duplicate found.

    :param web_testing_campaigns_json: Trimmed JSON string of web_testing_campaigns.
    :param context: User context used for debug metadata in the error log.
    :return: None; parsing continues after logging (last duplicate value wins).
    """
    # set to track the keys seen so far
    keys_seen_so_far = set()
    # iterate over the web testing campaigns json and log the first duplicate json object key
    for key_regex_match in _WEB_TESTING_JSON_STRING_KEY_REGEX.finditer(
        web_testing_campaigns_json
    ):
        object_key_name = key_regex_match.group(1)
        # if the object key name is already in the keys seen so far, then log an error
        if object_key_name in keys_seen_so_far:
            LogManager.get_instance().error_log(
                "INVALID_WEB_TESTING_CAMPAIGNS_DUPLICATE_KEY",
                {"duplicateKey": object_key_name},
                {
                    "an": ApiEnum.GET_FLAG.value,
                    "uuid": context.get_vwo_uuid(),
                    "sId": context.get_session_id(),
                },
            )
            return
        # add the object key name to the keys seen so far
        keys_seen_so_far.add(object_key_name)

def is_web_testing_campaigns_absent_or_null(context: ContextModel) -> bool:
    """
    Returns whether platform_variables.web_testing_campaigns is missing or explicitly null.

    :param context: User context that may carry platform_variables.
    :return: True if web_testing_campaigns is absent or null; otherwise False.
    """
    # get the platform variables
    platform_variables = context.get_platform_variables()
    # if the platform variables are not present, then return True
    if is_null(platform_variables) or not platform_variables:
        return True
    if not is_object(platform_variables):
        return True
    if "web_testing_campaigns" not in platform_variables:
        return True
    # get the web testing campaigns input
    web_testing_campaigns_input = platform_variables.get("web_testing_campaigns")
    # if the web testing campaigns input is None, then return True
    if is_null(web_testing_campaigns_input):
        return True
    return False

def dsl_contains_campaign_variation_node(segmentation_dsl: Any) -> bool:
    """
    Recursively checks whether a segmentation DSL tree contains a campaignVariation operator node.

    :param segmentation_dsl: Segmentation DSL object to walk (and/or/not/campaignVariation nodes).
    :return: True if any campaignVariation node exists in the tree; otherwise False.
    """
    # if the segmentation dsl is None or not a dictionary, then return False
    if is_null(segmentation_dsl) or not is_object(segmentation_dsl):
        return False

    # iterate over the segmentation dsl and check if it contains a campaign variation node
    for dsl_property_name in segmentation_dsl:
        # if the dsl property name is the campaign variation node, then return True
        if dsl_property_name == SegmentOperatorValueEnum.WEB_CAMPAIGN_VARIATION.value:
            return True

        nested_value = segmentation_dsl[dsl_property_name]
        if is_array(nested_value):
            for list_item in nested_value:
                if dsl_contains_campaign_variation_node(list_item):
                    return True
        elif is_object(nested_value):
            if dsl_contains_campaign_variation_node(nested_value):
                return True

    return False


def parse_web_testing_campaigns_from_context(
    context: ContextModel,
) -> Optional[Dict[str, str]]:
    """
    Parses context.platform_variables.web_testing_campaigns from a dict or JSON string into a normalized map.

    :param context: User context containing platform_variables.web_testing_campaigns.
    :return: Normalized campaign-to-variation map, or None if missing, invalid, or unparseable.
    """
    platform_variables = context.get_platform_variables()
    if is_null(platform_variables) or not platform_variables:
        return None
    if not is_object(platform_variables):
        return None

    web_testing_campaigns_raw = platform_variables.get("web_testing_campaigns")
    if is_null(web_testing_campaigns_raw):
        return None

    # if the web testing campaigns raw is an object map, normalize it.
    if is_object(web_testing_campaigns_raw):
        return normalize_web_testing_campaigns_map(web_testing_campaigns_raw)

    # if the web testing campaigns raw is a string, then parse the web testing campaigns
    if is_string(web_testing_campaigns_raw):
        trimmed_json_input = web_testing_campaigns_raw.strip()
        if trimmed_json_input == "":
            return None
        _log_first_duplicate_json_object_key_scan(trimmed_json_input, context)
        try:
            # parse the web testing campaigns as a json object
            parsed_json_object = json.loads(trimmed_json_input)
            # if the parsed json object is an object map, normalize it
            if is_object(parsed_json_object):
                return normalize_web_testing_campaigns_map(parsed_json_object)
            # if the parsed json object is not an object map, then log an error
            LogManager.get_instance().error_log(
                "INVALID_WEB_TESTING_CAMPAIGNS_JSON",
                {},
                {
                    "an": ApiEnum.GET_FLAG.value,
                    "uuid": context.get_vwo_uuid(),
                    "sId": context.get_session_id(),
                },
            )
        except json.JSONDecodeError:
            # if the json decode error is raised, then log an error
            LogManager.get_instance().error_log(
                "INVALID_WEB_TESTING_CAMPAIGNS_JSON",
                {},
                {
                    "an": ApiEnum.GET_FLAG.value,
                    "uuid": context.get_vwo_uuid(),
                    "sId": context.get_session_id(),
                },
            )
        return None

    # if the web testing campaigns raw is not an object or a string, then log an error
    value_kind_label = get_type(web_testing_campaigns_raw)
    LogManager.get_instance().error_log(
        "INVALID_WEB_TESTING_CAMPAIGNS_TYPE",
        {"kind": value_kind_label},
        {
            "an": ApiEnum.GET_FLAG.value,
            "uuid": context.get_vwo_uuid(),
            "sId": context.get_session_id(),
        },
    )
    return None

def evaluate_web_testing_campaign_variation(
    operand_encoding: str,
    campaigns_map: Optional[Dict[str, str]],
) -> Tuple[bool, bool]:
    """
    Evaluates a campaignVariation operand encoding against the user's web testing campaign assignments.

    :param operand_encoding: Encoded operand (e.g. "123", "123_2", "123_!2", "!123").
    :param campaigns_map: Normalized map of campaign ID to assigned variation ID, or None.
    :return: Tuple of (segment matched, operand encoding invalid).
    """
    if not is_string(operand_encoding):
        return (False, True)

    assignments_by_campaign_id = (
        campaigns_map if is_defined(campaigns_map) else {}
    )

    # e.g. "!123" — not in campaign 123 (no assignment for that campaign id).
    not_in_campaign_regex_match = re.match(r"^!(\d+)$", operand_encoding)
    if not_in_campaign_regex_match:
        campaign_id_digits = not_in_campaign_regex_match.group(1)
        exists_in_assignments_map = campaign_id_digits in assignments_by_campaign_id
        return (not exists_in_assignments_map, False)

    # e.g. "123_!3" — in campaign 123 but assigned variation is not 3.
    in_campaign_but_not_variation_regex_match = re.match(r"^(\d+)_!(\d+)$", operand_encoding)
    # if the operand encoding is a campaign and variation id, then check if the user is in the campaign but not the variation
    if in_campaign_but_not_variation_regex_match:
        campaign_id_digits = in_campaign_but_not_variation_regex_match.group(1)
        variation_id_digits = in_campaign_but_not_variation_regex_match.group(2)
        # if the campaign id is not in the assignments by campaign id, then return False and False
        if campaign_id_digits not in assignments_by_campaign_id:
            return (False, False)
        assigned_variation_id = assignments_by_campaign_id[campaign_id_digits]
        return (assigned_variation_id != variation_id_digits, False)

    # e.g. "123_3" — in campaign 123 with variation exactly 3.
    campaign_and_variation_regex_match = re.match(r"^(\d+)_(\d+)$", operand_encoding)
    if campaign_and_variation_regex_match:
        # if the campaign id is not in the assignments by campaign id, then return False
        campaign_id_digits = campaign_and_variation_regex_match.group(1)
        # get the variation id digits
        variation_id_digits = campaign_and_variation_regex_match.group(2)
        if campaign_id_digits not in assignments_by_campaign_id:
            return (False, False)
        assigned_variation_id = assignments_by_campaign_id[campaign_id_digits]
        return (assigned_variation_id == variation_id_digits, False)

    # e.g. "123" — in campaign 123 (any assigned variation counts).
    campaign_id_only_regex_match = re.match(r"^(\d+)$", operand_encoding)
    if campaign_id_only_regex_match:
        campaign_id_digits = campaign_id_only_regex_match.group(1)
        user_in_campaign = campaign_id_digits in assignments_by_campaign_id
        return (user_in_campaign, False)

    return (False, True)