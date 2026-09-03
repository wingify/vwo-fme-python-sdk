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

import random
from typing import Callable, Optional
from ..models.settings.settings_model import SettingsModel
from ..utils.internal_events_sampling_util import (
    should_apply_sampling,
    get_usage_stats_sampling_percent,
    get_debug_event_sampling_percent,
    passes_sampling_percent,
)

class InternalEventsSamplingService:
    """
    Applies sampling rules for internal SDK events:
    `vwo_sdkUsageStats` and sampled `vwo_sdkDebug`.
    """

    def __init__(self, random_value_provider: Optional[Callable[[], float]] = None):
        """
        Creates a sampling service.
        :param random_value_provider: Optional supplier returning a value in [0, 1) for sampling checks; overridable in tests.
        """
        self._random_value_provider = random_value_provider if random_value_provider is not None else random.random

    def should_send_usage_stats_event(self, settings: Optional[SettingsModel]) -> bool:
        """
        Determines whether the usage-stats event should be sent.
        On server, always sends unless `alwaysApplySampling.server` is enabled.
        :param settings: Parsed settings from the server
        :return: `True` when the usage-stats event should be sent
        """
        if not should_apply_sampling(settings):
            return True
        
        usage_stats_sampling_percent = get_usage_stats_sampling_percent(settings)
        return passes_sampling_percent(usage_stats_sampling_percent, self._random_value_provider())

    def should_send_sampled_debug_event(self, settings: Optional[SettingsModel]) -> bool:
        """
        Determines whether a sampled debug event should be sent.
        Only called for `msg_t` keys in the sampled set; always-send keys bypass this.
        :param settings: Parsed settings from the server
        :return: `True` when the sampled debug event should be sent
        """
        if not should_apply_sampling(settings):
            return True
        
        debug_sampling_percent = get_debug_event_sampling_percent(settings)
        return passes_sampling_percent(debug_sampling_percent, self._random_value_provider())
