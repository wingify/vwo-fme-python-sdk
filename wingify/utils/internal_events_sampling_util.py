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

import math
from typing import Optional
from ..constants.Constants import Constants
from ..constants.sampled_debug_error_template_keys import SampledDebugErrorTemplateKeys
from ..models.settings.settings_model import SettingsModel
from ..models.settings.internal_event_sampling_settings_model import PlatformSamplingRates

def get_default_sampling_percent() -> float:
    """
    Returns the default server sampling percentage when settings omit the value.
    :return: Default sampling percentage (10.0)
    """
    return Constants.INTERNAL_EVENTS_DEFAULT_SAMPLING_PERCENT_SERVER

def normalize_sampling_percent(sampling_value: Optional[float]) -> float:
    """
    Normalizes a sampling value to a valid percentage in the range [0, 100].
    Falls back to the server default when the value is missing or invalid.
    :param sampling_value: Raw value from settings
    :return: Valid sampling percentage between 0 and 100
    """
    if sampling_value is not None and 0 <= sampling_value <= 100:
        return float(sampling_value)
    
    return get_default_sampling_percent()

def get_runtime_sampling_percent(runtime_sampling_config: Optional[PlatformSamplingRates]) -> float:
    """
    Reads the server sampling percentage from a runtime sampling config object.
    :param runtime_sampling_config: Nested config (e.g. `sampling.usage`)
    :return: Sampling percentage for the server runtime
    """
    if runtime_sampling_config is None:
        return get_default_sampling_percent()
    
    return normalize_sampling_percent(runtime_sampling_config.get_server())

def get_usage_stats_sampling_percent(settings: Optional[SettingsModel]) -> float:
    """
    Reads the usage-stats sampling percentage for the server runtime from settings.
    :param settings: Parsed settings from the server
    :return: Configured usage-stats sampling percentage (0-100)
    """
    sampling = settings.get_sampling() if settings else None
    usage_sampling = sampling.get_usage() if sampling else None
    return get_runtime_sampling_percent(usage_sampling)

def get_debug_event_sampling_percent(settings: Optional[SettingsModel]) -> float:
    """
    Reads the debug-event sampling percentage for the server runtime from settings.
    :param settings: Parsed settings from the server
    :return: Configured debug sampling percentage (0-100)
    """
    sampling = settings.get_sampling() if settings else None
    debug_sampling = sampling.get_debug() if sampling else None
    return get_runtime_sampling_percent(debug_sampling)

def should_apply_sampling(settings: Optional[SettingsModel]) -> bool:
    """
    Determines whether sampling should be evaluated before send.
    Controlled by `alwaysApplySampling.server`; defaults to `False`.
    When `False`, usage-stats and sampled debug events are always sent.
    :param settings: Parsed settings from the server
    :return: `True` when a sampling check is required before sending
    """
    if settings is None:
        return Constants.INTERNAL_EVENTS_DEFAULT_ALWAYS_APPLY_SAMPLING

    always_apply_sampling = settings.get_always_apply_sampling()
    if always_apply_sampling is None or always_apply_sampling.get_server() is None:
        return Constants.INTERNAL_EVENTS_DEFAULT_ALWAYS_APPLY_SAMPLING

    return always_apply_sampling.get_server()

def passes_sampling_percent(sampling_percent: float, random_value: float) -> bool:
    """
    Evaluates whether an event qualifies under the configured sampling percentage.
    :param sampling_percent: Configured sampling percentage (0-100)
    :param random_value: Random value in the range [0, 1)
    :return: `True` when the random draw falls within the sampling threshold
    """
    # Map random [0,1) to integer percent bucket [0,100]
    normalized_random_percent = int(math.floor(random_value * 101))
    return normalized_random_percent <= sampling_percent

def is_sampled_debug_error_template_key(message_template_key: str) -> bool:
    """
    Checks whether a debug error template key is in the sampled set.
    :param message_template_key: The `msg_t` value from the debug event
    :return: `True` when the key requires sampling before send
    """
    return SampledDebugErrorTemplateKeys.contains(message_template_key)
