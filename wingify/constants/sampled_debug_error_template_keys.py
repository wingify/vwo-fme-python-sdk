# Copyright 2024-2026 Wingify Software Pvt. Ltd.
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

class SampledDebugErrorTemplateKeys:
    """
    Debug error template keys (`msg_t`) that are subject to sampling.
    Keys not listed here always send and bypass sampling.
    """
    SAMPLED_KEYS = {
        "EVENT_NOT_FOUND",
        "FEATURE_NOT_FOUND",
        "FEATURE_NOT_FOUND_WITH_ID"
    }

    @staticmethod
    def contains(message_template_key: str) -> bool:
        """
        Checks whether a debug error template key should be sampled before sending.

        :param message_template_key: The `msg_t` value from the debug event
        :return: `True` if the key is in the sampled set; `False` otherwise
        """
        return message_template_key is not None and message_template_key in SampledDebugErrorTemplateKeys.SAMPLED_KEYS
