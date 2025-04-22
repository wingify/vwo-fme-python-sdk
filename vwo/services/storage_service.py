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
from typing import Any, Dict
from ..enums.storage_enum import StorageEnum
from ..packages.storage.storage import Storage
from ..utils.data_type_util import is_null, is_undefined
from ..packages.logger.core.log_manager import LogManager
from ..utils.log_message_util import error_messages


class StorageService:
    def __init__(self):
        self.storage_data: Dict[str, Any] = {}

    def get_data_in_storage(
        self, feature_key: Any, context: ContextModel
    ) -> Dict[Any, Any]:
        storage_instance = Storage.get_instance().get_connector()

        if is_null(storage_instance) or is_undefined(storage_instance):
            return {"status": StorageEnum.STORAGE_UNDEFINED.value}

        try:
            data = storage_instance.get(feature_key, context.get_id())
            if data is None:
                return {"status": StorageEnum.NO_DATA_FOUND.value}
            return data
        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get("STORED_DATA_ERROR").format(err)
            )
            return {"status": StorageEnum.NO_DATA_FOUND.value}

    def set_data_in_storage(self, data: Dict[Any, Any]) -> bool:
        storage_instance = Storage.get_instance().get_connector()

        if is_null(storage_instance) or is_undefined(storage_instance):
            return False

        try:
            storage_instance.set(data)
            return True
        except Exception as err:
            LogManager.get_instance().error(f"Error storing data: {err}")
            return False
