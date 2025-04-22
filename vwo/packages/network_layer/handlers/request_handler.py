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


from ..models.request_model import RequestModel
from ..models.global_request_model import GlobalRequestModel
from typing import Optional


class RequestHandler:
    def create_request(
        self, request: RequestModel, config: GlobalRequestModel
    ) -> Optional[RequestModel]:
        if not config.get_base_url() and not request.get_url():
            return None

        request.set_url(request.get_url() or config.get_base_url())
        request.set_timeout(request.get_timeout() or config.get_timeout())
        request.set_body(request.get_body() or config.get_body())
        request.set_headers(request.get_headers() or config.get_headers())

        request_query_params = request.get_query()
        config_query_params = config.get_query()
        for key, value in config_query_params.items():
            if key not in request_query_params:
                request_query_params[key] = value

        request.set_query(request_query_params)
        return request
