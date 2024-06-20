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


from .models.settings.settings_model import SettingsModel
from .utils.settings_util import set_settings_and_add_campaigns_to_rules
from .services.url_service import UrlService
from .packages.logger.core.log_manager import LogManager
from .utils.log_message_util import info_messages, error_messages, debug_messages
from .services.hooks_manager import HooksManager
from .models.user.context_model import ContextModel
from .models.user.get_flag import GetFlag
from .api.get_flag_api import GetFlagApi
from .api.track_api import TrackApi
from .api.set_attribute_api import SetAttributeApi
from typing import Dict, Any
from .utils.data_type_util import is_string, is_object, is_boolean
from .services.settings_manager import SettingsManager


class VWOClient:
    _settings: SettingsModel = None
    original_settings: Dict = None

    def __init__(self, settings: str, options: Dict):
        self.options = options
        if settings is None or settings == {}:
            return
        set_settings_and_add_campaigns_to_rules(settings, self)
        UrlService(self._settings.get_collection_prefix())

        LogManager.get_instance().info(info_messages.get("CLIENT_INITIALIZED"))

    def get_flag(self, feature_key: str, context: Dict) -> GetFlag:
        """
        Retrieves the value of a feature flag for a given feature key and context.
        This method validates the feature key and context, ensures the settings are valid, and then uses the FlagApi to get the flag value.

        :param feature_key: The key of the feature to retrieve.
        :param context: The context in which the feature flag is being retrieved, must include a valid user ID.
        :return: The feature flag value.
        """
        api_name = "getFlag"
        get_flag_response = GetFlag()

        try:
            hook_manager = HooksManager(self.options)

            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=api_name)
            )

            # Validate featureKey is a string
            if not isinstance(feature_key, str):
                LogManager.get_instance().error(
                    error_messages.get("API_INVALID_PARAM").format(
                        apiName=api_name,
                        key=feature_key,
                        type=type(feature_key).__name__,
                        correctType="string",
                    )
                )
                raise TypeError("TypeError: featureKey should be a string")

            # Validate settings are loaded and valid
            if not SettingsManager.is_settings_valid(self.original_settings):
                LogManager.get_instance().error(
                    error_messages.get("API_SETTING_INVALID")
                )
                raise ValueError("Invalid Settings")

            # Validate user ID is present in context
            if not context or "id" not in context:
                LogManager.get_instance().error(
                    error_messages.get("API_CONTEXT_INVALID")
                )
                raise ValueError("Invalid context")

            context_model = ContextModel(context)

            # Fetch the feature flag value using FlagApi
            flag_api = GetFlagApi()
            data = flag_api.get(
                feature_key, self._settings, context_model, hook_manager
            )

            return data

        except (TypeError, ValueError) as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return get_flag_response

        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return get_flag_response

    def track_event(
        self, event_name: str, context: Dict, event_properties: Dict[str, Any] = {}
    ) -> Dict:
        """
        Tracks an event with specified properties and context.
        This method validates the types of the inputs and ensures the settings and user context are valid before proceeding.

        :param event_name: The name of the event to track.
        :param context: The context in which the event is being
        :param event_properties: The properties of the event.
        """
        api_name = "track_event"

        try:
            hook_manager = HooksManager(self.options)

            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=api_name)
            )

            # Validate featureKey is a string
            if not is_string(event_name):
                LogManager.get_instance().error(
                    error_messages.get("API_INVALID_PARAM").format(
                        apiName=api_name,
                        key="event_name",
                        type=type(event_name).__name__,
                        correctType="string",
                    )
                )
                raise TypeError("TypeError: event_name should be a string")

            if not is_object(event_properties):
                LogManager.get_instance().error(
                    error_messages.get("API_INVALID_PARAM").format(
                        apiName=api_name,
                        key="event_properties",
                        type=type(event_properties).__name__,
                        correctType="object",
                    )
                )
                raise TypeError("TypeError: event_properties should be an object")

            # Validate settings are loaded and valid
            if not SettingsManager.is_settings_valid(self.original_settings):
                LogManager.get_instance().error(
                    error_messages.get("API_SETTING_INVALID")
                )
                raise ValueError("Invalid Settings")

            # Validate user ID is present in context
            if not context or "id" not in context:
                LogManager.get_instance().error(
                    error_messages.get("API_CONTEXT_INVALID")
                )
                raise ValueError("Invalid context")

            context_model = ContextModel(context)

            # Fetch the feature flag value using FlagApi
            trackApi = TrackApi()
            data = trackApi.track(
                self._settings,
                event_name,
                context_model,
                event_properties,
                hook_manager,
            )

            return data

        except (TypeError, ValueError) as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return {event_name: False}

        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return {event_name: False}

    def set_attribute(self, attribute_key: str, attribute_value: Any, context: Dict):
        """
        Sets an attribute for a user in the context provided.
        This method validates the types of the inputs before proceeding with the API call.

        :param attribute_key: The key of the attribute to set.
        :param attribute_value: The value of the attribute to set.
        :param context: The context in which the attribute is being set.
        """
        api_name = "set_attribute"

        try:

            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=api_name)
            )

            # Validate featureKey is a string
            if not is_string(attribute_key):
                LogManager.get_instance().error(
                    error_messages.get("API_INVALID_PARAM").format(
                        apiName=api_name,
                        key="attribute_key",
                        type=type(attribute_key).__name__,
                        correctType="string",
                    )
                )
                raise TypeError("TypeError: attribute_key should be a string")

            if (
                not is_string(attribute_value)
                and not isinstance(attribute_value, int)
                and not isinstance(attribute_value, bool)
            ):
                LogManager.get_instance().error(
                    error_messages.get("API_INVALID_PARAM").format(
                        apiName=api_name,
                        key="attribute_value",
                        type=type(attribute_value).__name__,
                        correctType="string or int or bool",
                    )
                )
                raise TypeError(
                    "TypeError: attribute_value should be an string or int or bool"
                )

            # Validate settings are loaded and valid
            if not SettingsManager.is_settings_valid(self.original_settings):
                LogManager.get_instance().error(
                    error_messages.get("API_SETTING_INVALID")
                )
                raise ValueError("Invalid Settings")

            # Validate user ID is present in context
            if not context or "id" not in context:
                LogManager.get_instance().error(
                    error_messages.get("API_CONTEXT_INVALID")
                )
                raise ValueError("Invalid context")

            context_model = ContextModel(context)

            # Fetch the feature flag value using FlagApi
            set_attribute_api = SetAttributeApi()
            set_attribute_api.set_attribute(
                self._settings, attribute_key, attribute_value, context_model
            )
            return

        except (TypeError, ValueError) as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return

        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return
