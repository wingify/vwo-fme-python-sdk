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

import unittest
from wingify.constants.Constants import Constants
from wingify.models.settings.settings_model import SettingsModel
from wingify.services.internal_events_sampling_service import InternalEventsSamplingService
from wingify.utils import internal_events_sampling_util

class InternalEventsSamplingServiceTest(unittest.TestCase):
    """
    Unit tests for internal SDK event sampling.
    
    Covers two layers:
    - `internal_events_sampling_util` — reads DaCDN sampling config and evaluates pure sampling math
    - `InternalEventsSamplingService` — applies send/drop decisions for usage-stats and sampled debug events
    """

    def setUp(self):
        self.mock_sampling_settings = self.create_mock_sampling_settings()

    def create_mock_sampling_settings(self):
        """
        Builds a representative SettingsModel object for sampling tests.
        """
        data = {
            "accountId": 123456,
            "sdkKey": "test-sdk-key",
            "version": 1,
            "features": [],
            "campaigns": [],
            "sdkMetaInfo": {
                "wasInitializedEarlier": False
            },
            "sampling": {
                "usage": {"server": 20.0},
                "debug": {"server": 50.0}
            },
            "alwaysApplySampling": {
                "server": True
            }
        }
        return SettingsModel(data)

    def create_empty_settings(self):
        data = {
            "accountId": 123456,
            "sdkKey": "test-sdk-key",
            "version": 1,
            "features": [],
            "campaigns": []
        }
        return SettingsModel(data)

    # --- InternalEventsSamplingUtil: defaults and config parsing ---

    def test_server_default_sampling_is_used_when_value_missing(self):
        self.assertEqual(
            Constants.INTERNAL_EVENTS_DEFAULT_SAMPLING_PERCENT_SERVER,
            internal_events_sampling_util.get_default_sampling_percent()
        )
        self.assertEqual(10.0, internal_events_sampling_util.normalize_sampling_percent(None))
        self.assertEqual(10.0, internal_events_sampling_util.normalize_sampling_percent(150.0))

    def test_runtime_defaults_are_used_when_sampling_absent(self):
        empty_settings = self.create_empty_settings()
        self.assertEqual(10.0, internal_events_sampling_util.get_usage_stats_sampling_percent(empty_settings))
        self.assertEqual(10.0, internal_events_sampling_util.get_debug_event_sampling_percent(empty_settings))

    def test_usage_stats_sampling_is_read_for_server_runtime(self):
        self.assertEqual(20.0, internal_events_sampling_util.get_usage_stats_sampling_percent(self.mock_sampling_settings))

    def test_always_apply_sampling_server_is_read_from_settings(self):
        self.assertTrue(internal_events_sampling_util.should_apply_sampling(self.mock_sampling_settings))
        self.assertFalse(internal_events_sampling_util.should_apply_sampling(self.create_empty_settings()))

    # --- InternalEventsSamplingUtil: sampling math and debug key classification ---

    def test_sampling_passes_within_threshold(self):
        # 0.1 maps to bucket 10, which is within a 20% threshold
        self.assertTrue(internal_events_sampling_util.passes_sampling_percent(20.0, 0.1))

    def test_sampling_fails_above_threshold(self):
        # 0.99 maps to bucket 99, which exceeds a 20% threshold
        self.assertFalse(internal_events_sampling_util.passes_sampling_percent(20.0, 0.99))

    def test_sampled_debug_keys_are_detected(self):
        self.assertTrue(internal_events_sampling_util.is_sampled_debug_error_template_key("EVENT_NOT_FOUND"))
        self.assertTrue(internal_events_sampling_util.is_sampled_debug_error_template_key("FEATURE_NOT_FOUND"))

    def test_non_sampled_debug_keys_are_not_detected(self):
        self.assertFalse(internal_events_sampling_util.is_sampled_debug_error_template_key("INVALID_OPTIONS"))
        self.assertFalse(internal_events_sampling_util.is_sampled_debug_error_template_key("EXECUTION_FAILED"))
        self.assertFalse(internal_events_sampling_util.is_sampled_debug_error_template_key("NETWORK_CALL_FAILED"))
        self.assertFalse(internal_events_sampling_util.is_sampled_debug_error_template_key(""))

    # --- InternalEventsSamplingService: usage-stats send decisions ---

    def test_usage_stats_always_send_when_always_apply_sampling_false(self):
        sampling_service = InternalEventsSamplingService(lambda: 0.0)
        settings = self.create_empty_settings()
        settings._always_apply_sampling = type('AlwaysApplySampling', (object,), {'get_server': lambda self: False})()
        settings._sampling = type('EventCategorySamplingRates', (object,), {
            'get_usage': lambda self: type('PlatformSamplingRates', (object,), {'get_server': lambda self: 0.0})(),
            'get_debug': lambda self: None
        })()
        
        self.assertTrue(sampling_service.should_send_usage_stats_event(settings))

    def test_usage_stats_sampling_applies_when_always_apply_sampling_true(self):
        # random=1.0 always fails sampling; with 0% usage threshold the event is dropped
        sampling_service = InternalEventsSamplingService(lambda: 1.0)
        settings = self.create_empty_settings()
        settings._always_apply_sampling = type('AlwaysApplySampling', (object,), {'get_server': lambda self: True})()
        settings._sampling = type('EventCategorySamplingRates', (object,), {
            'get_usage': lambda self: type('PlatformSamplingRates', (object,), {'get_server': lambda self: 0.0})(),
            'get_debug': lambda self: None
        })()

        self.assertFalse(sampling_service.should_send_usage_stats_event(settings))

    # --- InternalEventsSamplingService: sampled debug send decisions ---

    def test_sampled_debug_events_always_send_when_always_apply_sampling_false(self):
        sampling_service = InternalEventsSamplingService(lambda: 1.0)
        settings = self.create_empty_settings()
        settings._always_apply_sampling = type('AlwaysApplySampling', (object,), {'get_server': lambda self: False})()
        settings._sampling = type('EventCategorySamplingRates', (object,), {
            'get_usage': lambda self: None,
            'get_debug': lambda self: type('PlatformSamplingRates', (object,), {'get_server': lambda self: 0.0})()
        })()

        self.assertTrue(sampling_service.should_send_sampled_debug_event(settings))

    def test_sampled_debug_events_apply_debug_sampling_when_always_apply_sampling_true(self):
        # mock_sampling_settings has debug.server=50%, alwaysApplySampling.server=True; random=0.0 always passes
        sampling_service = InternalEventsSamplingService(lambda: 0.0)
        self.assertTrue(sampling_service.should_send_sampled_debug_event(self.mock_sampling_settings))

    def test_sampled_debug_events_blocked_when_always_apply_sampling_true_and_sampling_zero(self):
        sampling_service = InternalEventsSamplingService(lambda: 1.0)
        settings = self.create_empty_settings()
        settings._always_apply_sampling = type('AlwaysApplySampling', (object,), {'get_server': lambda self: True})()
        settings._sampling = type('EventCategorySamplingRates', (object,), {
            'get_usage': lambda self: None,
            'get_debug': lambda self: type('PlatformSamplingRates', (object,), {'get_server': lambda self: 0.0})()
        })()

        self.assertFalse(sampling_service.should_send_sampled_debug_event(settings))
