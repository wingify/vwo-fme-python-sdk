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


from ..models.global_request_model import GlobalRequestModel
from ..models.request_model import RequestModel
from ..models.response_model import ResponseModel
from ..handlers.request_handler import RequestHandler
from ..client.network_client import NetworkClient
from ...logger.core.log_manager import LogManager
from ....utils.log_message_util import error_messages
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Any
from ....constants.Constants import Constants


class NetworkManager:
    _instance = None

    def __init__(self, threading: Dict[str, Any] = None):
        self.client = None
        self.config = None
        self.should_use_threading = threading.get(
            "enabled", Constants.SHOULD_USE_THREADING
        )
        self.thread_pool_max_workers = threading.get(
            "max_workers", Constants.THREAD_POOL_MAX_WORKERS
        )

    def set_config(self, config: GlobalRequestModel):
        self.config = config

    def get_config(self) -> GlobalRequestModel:
        return self.config

    def attach_client(self):
        self.client = NetworkClient()
        self.config = GlobalRequestModel()

    @classmethod
    def get_instance(cls, threading: Dict[str, Any] = None) -> "NetworkManager":
        if cls._instance is None:
            cls._instance = cls(threading)
        return cls._instance

    def create_request(self, request: RequestModel) -> RequestModel:
        return RequestHandler().create_request(request, self.config)

    def get(self, request: RequestModel) -> ResponseModel:
        request_model = self.create_request(request)
        if not request_model or not request_model.get_url():
            response = ResponseModel()
            response.set_error("No URL found")
            return response
        return self.client.get(request_model)

    def post(self, request: RequestModel) -> ResponseModel:
        request_model = self.create_request(request)
        if not request_model or not request_model.get_url():
            response = ResponseModel()
            response.set_error("No URL found")
            return response
        return self.client.post(request_model)

        # Generic function to handle background task execution with ThreadPoolExecutor
    def execute_in_background(self, func: Callable):
        executor = ThreadPoolExecutor(max_workers=self.thread_pool_max_workers)
        executor.submit(func)