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

"""Legacy VWO facade — thin wrapper over the Wingify core."""

from typing import Dict, Optional

from wingify.wingify import Wingify, getUUID
from wingify.wingify import init as _wingify_init
from wingify.wingify_builder import WingifyBuilder
from wingify.wingify_client import WingifyClient


class VWO:
    """Legacy static orchestrator. Delegates to Wingify."""

    vwo_builder: WingifyBuilder = None
    instance: WingifyClient = None

    def __init__(self, options: Dict):
        VWO.set_instance(options)

    @staticmethod
    def set_instance(options: Dict) -> WingifyClient:
        options = dict(options or {})
        options["is_via_vwo"] = True
        instance = Wingify.set_instance(options)
        VWO.vwo_builder = Wingify.wingify_builder
        VWO.instance = instance
        return instance

    @staticmethod
    def getInstance() -> Optional[WingifyClient]:
        return Wingify.getInstance()


def init(options: Dict) -> Optional[WingifyClient]:
    """Initialize via legacy VWO entry — sets is_via_vwo for VWO hosts and branding."""
    options = dict(options or {})
    options["is_via_vwo"] = True
    return _wingify_init(options)


VWOClient = WingifyClient
VWOBuilder = WingifyBuilder

__all__ = ["VWO", "init", "getUUID", "VWOClient", "VWOBuilder"]
