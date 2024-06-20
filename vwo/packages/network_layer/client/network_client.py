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


from ..models.request_model import RequestModel
from ..models.response_model import ResponseModel
import requests
import json

class NetworkClient:
    def __init__(self):
        self.session = requests.Session()

    def get(self, request_model: RequestModel) -> ResponseModel:
        response_model = ResponseModel()
        try:
            options = request_model.get_options()
            response = self.session.get(options['url'], headers=options.get('headers'), timeout=options.get('timeout'))
            response_model.set_status_code(response.status_code)
            response_model.set_headers(response.text)
            if response.headers.get('Content-Type', '').startswith('application/json'):
                response_model.set_data(response.json())
            else:
                response_model.set_data(response.text)
        except Exception as e:
            response_model.set_error(str(e))
        return response_model

    def post(self, request_model: RequestModel) -> ResponseModel:
        response_model = ResponseModel()
        try:
            options = request_model.get_options()
            response = self.session.post(options['url'], json=options.get('json'), headers=options.get('headers'), timeout=options.get('timeout'))
            response_model.set_status_code(response.status_code)
            response_model.set_headers(response.headers)
            if response.headers.get('Content-Type', '').startswith('application/json'):
                response_model.set_data(response.json())
            else:
                response_model.set_data(response.text)
        except Exception as e:
            response_model.set_error(str(e))
        return response_model
