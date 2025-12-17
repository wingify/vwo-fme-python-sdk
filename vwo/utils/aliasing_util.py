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


from typing import Any, Dict, List
import json

from ..enums.url_enum import UrlEnum
from ..services.settings_manager import SettingsManager
from ..utils.log_message_util import error_messages
from ..models.Alias import Alias
from ..models.AliasSetResponse import AliasSetResponse
from ..constants.Constants import Constants
from ..utils.gateway_service_util import get_from_gateway_service, post_to_gateway_service
from ..models.user.context_model import ContextModel

def get_alias(context: ContextModel) -> str:
    """
    Get the alias for the given user ID.

    :param context: The context to get the alias for.
    :return: The alias for the given user ID.
    """
    params: Dict[str, Any] = {
        "accountId": str(SettingsManager.get_instance().get_account_id()),
        "sdkKey": SettingsManager.get_instance().get_sdk_key(),
    }

    # gateway expects JSON array for userId
    user_id_json = json.dumps([context.get_id()])
    params[Constants.KEY_USER_ID] = user_id_json

    response = get_from_gateway_service(params, UrlEnum.GET_ALIAS.value, context)
    if not response:
        raise RuntimeError(
            error_messages.get("ERROR_GETTING_ALIAS").format(userId=context.get_id(), err="Response is null")
        )

    try:
        data_list: List[Dict[str, Any]] = json.loads(response) if isinstance(response, str) else response
    except Exception as exc:
        raise RuntimeError(
            error_messages.get("ERROR_GETTING_ALIAS").format(userId=context.get_id(), err="Invalid JSON response")
        ) from exc

    alias_objects = [Alias(item) for item in data_list or []]
    for item in alias_objects:
        if item.get_alias() == context.get_id():
            return item.get_user_id() or context.get_id()

    return context.get_id()


def set_alias(user_id: str, alias_id: str) -> bool:
    """
    Set the alias for the given user ID.

    :param user_id: The user ID to set the alias for.
    :param alias_id: The alias ID to set for the given user ID.
    :return: True if the alias is set successfully, False otherwise.
    """
    params: Dict[str, Any] = {
        "accountId": str(SettingsManager.get_instance().get_account_id()),
        "sdkKey": SettingsManager.get_instance().get_sdk_key(),
        Constants.KEY_USER_ID: user_id,
        Constants.KEY_ALIAS_ID: alias_id,
    }

    payload: Dict[str, Any] = {Constants.KEY_USER_ID: user_id, Constants.KEY_ALIAS_ID: alias_id}

    response = post_to_gateway_service(params, payload, UrlEnum.SET_ALIAS.value)
    if not response:
        raise RuntimeError(error_messages.get("ERROR_SETTING_ALIAS").format(userId=user_id))

    try:
        data = json.loads(response) if isinstance(response, str) else response
    except Exception as exc:
        raise RuntimeError(error_messages.get("ERROR_SETTING_ALIAS").format(userId=user_id)) from exc

    alias_set_response = AliasSetResponse(data)
    if alias_set_response.get_is_alias_set():
        return True

    raise RuntimeError(error_messages.get("ERROR_SETTING_ALIAS").format(userId=user_id))

def get_alias_user_id(context: ContextModel) -> str:
    """
    Get the user id from the gateway service when aliasing is enabled.

    :param context: The context to get the user id from.
    :return: The resolved user id (alias mapping applied if available).
    :raises RuntimeError: If gateway service is not provided when aliasing is enabled.
    """
    settings = SettingsManager.get_instance()
    if settings and settings.is_gateway_service_provided:
        return get_alias(context)
    raise RuntimeError("Valid Gateway service is required when aliasing is enabled")
