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

import time
import random
import requests
from ..models.request_model import RequestModel
from ..models.response_model import ResponseModel
from ....constants.Constants import Constants
from ...logger.core.log_manager import LogManager
from ....utils.log_message_util import error_messages
from ....enums.event_enum import EventEnum

class NetworkClient:
    """
    NetworkClient is a class that handles the network requests for the VWO SDK.
    """
    def __init__(self):
        self.session = requests.Session()
        self.max_retries = Constants.MAX_RETRIES
        self.initial_wait_time = Constants.INITIAL_WAIT_TIME

    def get(self, request_model: RequestModel) -> ResponseModel:
        """
        Sends a GET request to the specified URL.

        Args:
        :param request_model: The request model containing the URL and headers.
        :return: The response model containing the status code, headers, and data.
        """
        response_model = ResponseModel()
        options = request_model.get_options()
        for attempt in range(0, self.max_retries + 1):
            try:
                response = self.session.get(
                    options["url"],
                    headers=options.get("headers"),
                    timeout=options.get("timeout"),
                )
                response_model.set_status_code(response.status_code)
                response_model.set_headers(response.headers)

                if response.headers.get("Content-Type", "").startswith(
                    "application/json"
                ):
                    response_model.set_data(response.json())
                else:
                    response_model.set_data(response.text)

                # If the response is 400, it means the request is invalid and we should return the error
                if response.status_code == 400:
                    response_model.set_error(response.text)
                    return response_model
                if response.status_code < 200 or response.status_code >= 300:
                    raise requests.HTTPError(f"HTTP {response.status_code} error {response.text}")

                return response_model

            except (
                requests.Timeout,
                requests.ConnectionError,
                requests.HTTPError,
            ) as e:
                response_model.set_error(str(e))
                response_model.set_total_attempts(attempt)

                if attempt == self.max_retries:
                    LogManager.get_instance().error(
                        error_messages.get("NETWORK_CALL_RETRY_FAILED").format(
                            endPoint=options["url"], err=str(e)
                        )
                    )
                    return response_model

                sleep_time = self.initial_wait_time * (2 ** (attempt)) + (
                    0.5 * random.random()
                )
                LogManager.get_instance().error(
                    error_messages.get("ATTEMPTING_RETRY_FOR_FAILED_NETWORK_CALL").format(
                        endPoint=options["url"],
                        err=str(e),
                        delay=round(sleep_time, 2),
                        attempt=attempt + 1,
                        maxRetries=self.max_retries,
                    )
                )
                time.sleep(sleep_time)
        return response_model

    def post(self, request_model: RequestModel) -> ResponseModel:
        """
        Sends a POST request to the specified URL.

        Args:
            request_model: The request model containing the URL and headers.
        :return: The response model containing the status code, headers, and data.
        """
        response_model = ResponseModel()
        options = request_model.get_options()

        for attempt in range(0, self.max_retries + 1):
            try:
                response = self.session.post(
                    options["url"],
                    json=options.get("json"),
                    headers=options.get("headers"),
                    timeout=options.get("timeout"),
                )
                response_model.set_status_code(response.status_code)
                response_model.set_headers(response.headers)

                if response.headers.get("Content-Type", "").startswith(
                    "application/json"
                ):
                    response_model.set_data(response.json())
                else:
                    response_model.set_data(response.text)

                # If the response is 400, it means the request is invalid and we should return the error
                if response.status_code == 400:
                    response_model.set_error(response.text)
                    return response_model

                if response.status_code < 200 or response.status_code >= 300:
                    raise requests.HTTPError(f"HTTP {response.status_code} error {response.text}")
        
                return response_model

            except (
                requests.Timeout,
                requests.ConnectionError,
                requests.HTTPError,
            ) as e:
                response_model.set_error(str(e))
                response_model.set_total_attempts(attempt)
                if EventEnum.VWO_LOG_EVENT.value in options["url"]:
                    return response_model

                if attempt == self.max_retries:
                    LogManager.get_instance().error(
                        error_messages.get("NETWORK_CALL_RETRY_FAILED").format(
                            endPoint=options["url"], err=str(e)
                        )
                    )
                    return response_model

                sleep_time = self.initial_wait_time * (2 ** (attempt)) + (
                    0.5 * random.random()
                )
                LogManager.get_instance().error(
                    error_messages.get("ATTEMPTING_RETRY_FOR_FAILED_NETWORK_CALL").format(
                        endPoint=options["url"],
                        err=str(e),
                        delay=round(sleep_time, 2),
                        attempt=attempt + 1,
                        maxRetries=self.max_retries,
                    )
                )
                time.sleep(sleep_time)
        return response_model
