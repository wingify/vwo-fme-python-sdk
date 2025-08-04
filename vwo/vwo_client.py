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


from vwo.services.batch_event_queue import BatchEventQueue
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
    batch_event_queue: BatchEventQueue = None 
    _vwo_client_instance = None

    def __init__(self, settings: str, options: Dict):
        self.options = options
        if settings is None or settings == {}:
            return
        set_settings_and_add_campaigns_to_rules(settings, self)

        # Set the singleton instance to the current instance
        if VWOClient._vwo_client_instance is None:
            VWOClient._vwo_client_instance = self
        
        UrlService(self._settings.get_collection_prefix())

        LogManager.get_instance().info(info_messages.get("CLIENT_INITIALIZED"))
    
    @staticmethod
    def get_instance():
        """
        This method is used to get the singleton instance of the VWOClient.
        """
        return VWOClient._vwo_client_instance
    
    # Getter for the batch_event_queue
    def get_batch_event_queue(self):
        return self._batch_event_queue  

    # Setter for the batch_event_queue
    def set_batch_event_queue(self, value):
        self._batch_event_queue = value  
        

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
            settings_manager = SettingsManager.get_instance()
            if not settings_manager or not settings_manager.is_settings_valid(self.original_settings):
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
            settings_manager = SettingsManager.get_instance()
            if not settings_manager or not settings_manager.is_settings_valid(self.original_settings):
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

    def set_attribute(
        self, key_or_map: Any, value_or_context: Any, context: Dict = None
    ):
        """
        Sets an attribute for a user in the context provided.
        This method can be called in two ways:
        1. set_attribute(key, value, context) - Sets a single attribute
        2. set_attribute(attribute_map, context) - Sets multiple attributes

        The attribute values must be either strings, integers, or booleans.

        :param key_or_map: Either the attribute key (str) or a map of attributes (Dict)
        :param value_or_context: Either the attribute value or the context (if key_or_map is a Dict)
        :param context: The context in which the attribute is being set (only used when setting single attribute)
        """
        api_name = "set_attribute"

        try:
            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=api_name)
            )

            # Determine which calling pattern is being used
            if context is not None:
                # Single attribute pattern: (key, value, context)
                if not is_string(key_or_map):
                    LogManager.get_instance().error(
                        error_messages.get("API_INVALID_PARAM").format(
                            apiName=api_name,
                            key="key",
                            type=type(key_or_map).__name__,
                            correctType="string",
                        )
                    )
                    raise TypeError("TypeError: key should be a string")

                if not isinstance(value_or_context, (str, int, bool, float)):
                    LogManager.get_instance().error(
                        error_messages.get("API_INVALID_PARAM").format(
                            apiName=api_name,
                            key="value",
                            type=type(value_or_context).__name__,
                            correctType="string, integer, float, or boolean",
                        )
                    )
                    raise TypeError(
                        "TypeError: value should be a string, integer, float, or boolean"
                    )

                attribute_map = {key_or_map: value_or_context}
                user_context = context
            else:
                # Multiple attributes pattern: (attribute_map, context)
                if not is_object(key_or_map) or not key_or_map:
                    LogManager.get_instance().error(
                        error_messages.get("API_INVALID_PARAM").format(
                            apiName=api_name,
                            key="attribute_map",
                            type=type(key_or_map).__name__,
                            correctType="object",
                        )
                    )
                    raise TypeError(
                        "TypeError: attribute_map should be a non-empty object"
                    )

                # Validate all keys and values in the attribute map
                for key, value in key_or_map.items():
                    if not is_string(key):
                        LogManager.get_instance().error(
                            error_messages.get("API_INVALID_PARAM").format(
                                apiName=api_name,
                                key="key",
                                type=type(key).__name__,
                                correctType="string",
                            )
                        )
                        raise TypeError("TypeError: key should be a string")
                    if not isinstance(value, (str, int, bool, float)):
                        LogManager.get_instance().error(
                            error_messages.get("API_INVALID_PARAM").format(
                                apiName=api_name,
                                key=f"value for key '{key}'",
                                type=type(value).__name__,
                                correctType="string, integer, float, or boolean",
                            )
                        )
                        raise TypeError(
                            f"TypeError: value for key '{key}' should be a string, integer, float or boolean"
                        )

                attribute_map = key_or_map
                user_context = value_or_context

            # Validate settings are loaded and valid
            settings_manager = SettingsManager.get_instance()
            if not settings_manager or not settings_manager.is_settings_valid(self.original_settings):
                LogManager.get_instance().error(
                    error_messages.get("API_SETTING_INVALID")
                )
                raise ValueError("Invalid Settings")

            if not user_context or "id" not in user_context:
                LogManager.get_instance().error(
                    error_messages.get("API_CONTEXT_INVALID")
                )
                raise ValueError("Invalid context")

            context_model = ContextModel(user_context)

            set_attribute_api = SetAttributeApi()
            set_attribute_api.set_attribute(
                self._settings, attribute_map, context_model
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

    def update_settings(self, settings: Dict = None, is_via_webhook=True):
        """
        Updates the settings for the client.
        :param settings: The settings to update.
        :param is_via_webhook: Whether the settings are being updated via webhook.
        """

        api_name = "update_settings"

        try:
            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=api_name)
            )

            # check if settings are None or empty
            settings_to_update = settings
            if settings_to_update is None or settings_to_update == {}:
                # fetch the latest settings
                settings_to_update = SettingsManager.get_instance().fetch_settings(
                    is_via_webhook
                )

            # validate the settings
            settings_manager = SettingsManager.get_instance()
            if not settings_manager or not settings_manager.is_settings_valid(settings_to_update):
                LogManager.get_instance().error(
                    error_messages.get("API_SETTING_INVALID")
                )
                raise ValueError("TypeError: Invalid Settings schema")

            # update the settings
            set_settings_and_add_campaigns_to_rules(settings_to_update, self)
            LogManager.get_instance().info(
                info_messages.get("SETTINGS_UPDATED").format(
                    apiName=api_name, isViaWebhook=is_via_webhook
                )
            )
            return

        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("SETTINGS_FETCH_FAILED").format(
                    apiName=api_name, isViaWebhook=is_via_webhook, err=str(err)
                )
            )
            return
    
    
    def flush_events(self):
        """
        Flushes events from the batch event queue and clears the queue.
        This method will also handle calling the flush callback upon completion.
        """
        api_name = "flush_events"
        try:
            # Log that the API has been called
            LogManager.get_instance().debug(
                debug_messages.get("API_CALLED").format(apiName=api_name)
            )
            
            if self.batch_event_queue:
                LogManager.get_instance().debug(
                    f"Flushing events for accountId: {self.options.get('account_id')}. Queue size: {len(self.batch_event_queue.batch_queue)}"
                )
                # Trigger the flush and clear the queue
                flush_result = self.batch_event_queue.flush_and_clear_timer()
                return flush_result
            else:
                LogManager.get_instance().error(
                    f"Cannot flush events. Batch event queue is empty for accountId: {self.options.get('account_id')}"
                )
                return False

        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("API_THROW_ERROR").format(
                    apiName=api_name, err=str(err)
                )
            )
            return False
