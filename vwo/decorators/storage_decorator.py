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


from ..models.user.context_model import ContextModel
from ..enums.storage_enum import StorageEnum
from ..models.campaign.variation_model import VariationModel
from typing import Any, Dict, Optional
from ..services.storage_service import StorageService
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import error_messages


class StorageDecorator:
    def get_feature_from_storage(
        self, feature_key: str, context: ContextModel, storage_service: StorageService
    ) -> Any:
        campaign_map = storage_service.get_data_in_storage(feature_key, context)

        if campaign_map.get("status") == StorageEnum.STORAGE_UNDEFINED.value:
            return None  # No storage defined
        elif campaign_map.get("status") == StorageEnum.NO_DATA_FOUND.value:
            return None  # No data found in storage
        elif campaign_map.get("status") == StorageEnum.INCORRECT_DATA.value:
            return StorageEnum.INCORRECT_DATA.value  # Incorrect data found
        elif campaign_map.get("status") == StorageEnum.CAMPAIGN_PAUSED.value:
            return None  # Campaign is paused
        elif campaign_map.get("status") == StorageEnum.VARIATION_NOT_FOUND.value:
            return StorageEnum.VARIATION_NOT_FOUND.value  # No variation found
        elif campaign_map.get("status") == StorageEnum.WHITELISTED_VARIATION.value:
            return None  # Whitelisted variation, handle accordingly
        else:
            return campaign_map  # Valid data found, return it

    def set_data_in_storage(
        self, data: Dict[Any, Any], storage_service: StorageService
    ) -> Optional[VariationModel]:
        feature_key = data.get("featureKey")
        context = data.get("context")

        if not feature_key:
            LogManager.get_instance().error(
                error_messages.get(
                    error_messages.get("STORED_DATA_ERROR").format(key="featureKey")
                )
            )
            return None  # Invalid feature key, return None

        if not context or not context.get_id():
            LogManager.get_instance().error(
                error_messages.get(
                    error_messages.get("STORED_DATA_ERROR").format(
                        key="Context or Context.id"
                    )
                )
            )
            return None  # Invalid user ID, return None

        if (
            data.get("rolloutKey")
            and not data.get("experimentKey")
            and not data.get("rolloutVariationId")
        ):
            LogManager.get_instance().error(
                error_messages.get(
                    error_messages.get("STORED_DATA_ERROR").format(
                        key="Context or Context.id"
                    )
                )
            )
            return None  # Invalid rollout variation, return None

        if data.get("experimentKey") and not data.get("experimentVariationId"):
            LogManager.get_instance().error(
                error_messages.get(
                    error_messages.get("STORED_DATA_ERROR").format(
                        key="Variation:(rolloutKey, experimentKey or rolloutVariationId)"
                    )
                )
            )
            return None  # Invalid experiment variation, return None

        success = storage_service.set_data_in_storage(
            {
                "featureKey": feature_key,
                "userId": context.get_id(),
                "rolloutId": data.get("rolloutId"),
                "rolloutKey": data.get("rolloutKey"),
                "rolloutVariationId": data.get("rolloutVariationId"),
                "experimentId": data.get("experimentId"),
                "experimentKey": data.get("experimentKey"),
                "experimentVariationId": data.get("experimentVariationId"),
            }
        )

        if success:
            return True
        else:
            return None
