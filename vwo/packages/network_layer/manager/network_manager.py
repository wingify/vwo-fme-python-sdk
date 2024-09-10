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


from ..models.global_request_model import GlobalRequestModel
from ..models.request_model import RequestModel
from ..models.response_model import ResponseModel
from ..handlers.request_handler import RequestHandler
from ..client.network_client import NetworkClient
import aiohttp
from ...logger.core.log_manager import LogManager
from ....utils.log_message_util import error_messages

class NetworkManager:
    _instance = None
    def __init__(self):
        self.client = None
        self.config = None

    def set_config(self, config: GlobalRequestModel):
        self.config = config

    def get_config(self) -> GlobalRequestModel:
        return self.config
    
    def attach_client(self):
        self.client = NetworkClient()
        self.config = GlobalRequestModel()
    
    @classmethod
    def get_instance(cls) -> 'NetworkManager':
        if cls._instance is None:
            cls._instance = cls()
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
    
    async def post_async(self, request: RequestModel):
        try:
            options = request.get_options()
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        options['url'],
                        json=options.get('json'),
                        headers=options.get('headers'),
                        timeout=options.get('timeout')
                ) as response:
                    return response.status
        except Exception as err:
            LogManager.get_instance().error(
                error_messages.get('NETWORK_CALL_FAILED').format(
                    method='POST',
                    err=err,
                )
            )
