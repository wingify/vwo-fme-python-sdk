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

from typing import Dict, Any, Optional

class PlatformSamplingRates:
    """
    Holds the sampling percentage for a specific platform (e.g., server).
    Maps to the per-platform object inside `sampling.usage` or `sampling.debug`.
    """
    def __init__(self, data: Dict[str, Any]):
        self._server = data.get("server")

    def get_server(self) -> Optional[float]:
        return self._server

class EventCategorySamplingRates:
    """
    Groups sampling rates by event category: `usage` and `debug`.
    Maps to the top-level `sampling` object in the DaCDN settings.
    """
    def __init__(self, data: Dict[str, Any]):
        self._usage = PlatformSamplingRates(data.get("usage", {})) if data.get("usage") else None
        self._debug = PlatformSamplingRates(data.get("debug", {})) if data.get("debug") else None

    def get_usage(self) -> Optional[PlatformSamplingRates]:
        return self._usage

    def get_debug(self) -> Optional[PlatformSamplingRates]:
        return self._debug

class AlwaysApplySampling:
    """
    Controls whether sampling is enforced before sending an event.
    Maps to `alwaysApplySampling` in DaCDN settings.
    When `server` is False (the default), usage-stats and sampled debug events bypass sampling and are always sent.
    """
    def __init__(self, data: Dict[str, Any]):
        self._server = data.get("server")

    def get_server(self) -> Optional[bool]:
        return self._server
