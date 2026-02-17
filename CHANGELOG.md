# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.19.0] - 2026-02-17

- Added support to use the context `id` as the visitor UUID instead of auto-generating one. You can read the visitor UUID from the flag result via `flag.get_uuid()` (e.g. to pass to the web client).

Example usage:

```python
from vwo import init

# Initialize the SDK
vwo_client = init({
    "account_id": "123456",
    "sdk_key": "32-alpha-numeric-sdk-key",
})

# Default: SDK generates a UUID from id and account
context_with_generated_uuid = {"id": "user-123"}
flag1 = vwo_client.get_flag("feature-key", context_with_generated_uuid)

# Use your own UUID (e.g. from web client) by passing a valid web UUID as id
context_with_custom_uuid = {
    "id": "D7E2EAA667909A2DB8A6371FF0975C2A5",  # your existing UUID
}
flag2 = vwo_client.get_flag("feature-key", context_with_custom_uuid)

# Get the UUID from the flag result (e.g. to pass to web client)
uuid = flag1.get_uuid()
print("Visitor UUID:", uuid)
```

## [1.18.0] - 2026-02-05

### Added

- Added session management capabilities to enable integration with VWO's web client testing campaigns. The SDK now automatically generates and manages session IDs to connect server-side feature flag decisions with client-side user sessions.

  Example usage:

  ```python
  from vwo import init

  options = {
      'sdk_key': '32-alpha-numeric-sdk-key',
      'account_id': '123456',
  }

  vwo_client = init(options)

  # Session ID is automatically generated if not provided
  context = {'id': 'user-123'}
  flag = vwo_client.get_flag('feature-key', context)

  # Access the session ID to pass to web client for session recording
  session_id = flag.get_session_id()
  print(f"Session ID for web client: {session_id}")
  ```

  You can also explicitly set a session ID to match a web client session:

  ```python
  from vwo import init

  vwo_client = init(options)

  context = {
    'id': 'user-123',
    'session_id': 1697123456  # Custom session ID matching web client
  }

  flag = vwo_client.get_flag('feature-key', context)
  ```

  This enhancement enables seamless integration between server-side feature flag decisions and client-side session recording, allowing for comprehensive user behavior analysis across both server and client environments.

## [1.17.0] - 2025-01-08

### Added

- Added support for redirecting all network calls through a custom proxy URL. This feature allows users to route all SDK network requests (settings, tracking, etc.) through their own proxy server.

```python
options = {
  'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
  'account_id': '123456', # VWO Account ID
  'proxy_url': 'https://custom.proxy.com'
}

vwo_client = init(options)
```

**Note:** If both `gateway_service` and `proxy_url` are provided, the SDK will give preference to the `gateway_service` for all network requests.


## [1.16.0] - 2025-12-16

### Added
- Add support for user aliasing (will work after gateway has been setup)

  ```python
  from vwo import init

  options = {
      'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
      'account_id': '123456', # VWO Account ID
      # set gateway service
      'gateway_service': {
          'url': 'http://custom.gateway.com'
      },
      # enable aliasing
      'is_aliasing_enabled': True,
  }

  vwo_client = init(options)
  ```

  You can also call `set_alias` for a given `user_id` and `alias_id`

  ```python
  is_alias_set = vwo_client.set_alias('user-id-1', 'alias-id-1')
  ```

  Now if you call the `get_flag` again for id - `alias-id-1`, the `user-id-1` will be used for evaluation.

## [1.15.0] - 2025-11-20

### Added

- Added batch event processing to optimize network calls during GetFlag operations. Multiple impression events are now collected and sent in a single batch request

## [1.14.0] - 2025-11-17

### Added

- Enhanced Logging capabilities at VWO by sending `vwo_sdkDebug` event with additional debug properties.

## [1.13.0] - 2025-09-04

### Added

- Post-segmentation variables are now automatically included as unregistered attributes, enabling post-segmentation without requiring manual setup.
- Added support for built-in targeting conditions, including browser version, OS version, and IP address, with advanced operator support (greaterThan, lessThan, regex).

## [1.12.0] - 2025-09-02

### Added

- Sends usage statistics to VWO servers automatically during SDK initialization

## [1.11.0] - 2025-07-21

### Added

- Added support for sending a one-time initialization event to the server to verify correct SDK setup.

## [1.10.1] - 2025-07-24

### Added

- Send the SDK name and version in the settings call to VWO as query parameters.

## [1.10.0] - 2025-07-02

### Added

- Added exponential backoff retry mechanism for failed network requests. This improves reliability by automatically retrying failed requests with increasing delays between attempts.

## [1.9.1] - 2025-05-07

### Added

- Added a feature to track and collect usage statistics related to various SDK features and configurations which can be useful for analytics, and gathering insights into how different features are being utilized by end users.

## [1.9.0] - 2025-05-06

### Added

- Added support for `batch_event_data` configuration to optimize network requests by batching multiple events together. This allows you to:

  - Configure `request_time_interval` to flush events after a specified time interval
  - Set `events_per_request` to control maximum events per batch
  - Implement `flush_callback` to handle batch processing results
  - Manually trigger event flushing via `flush_events()` method

  ```python
  from vwo import init

  def event_flush_callback(error, payload):
        # your implementation here

  options = {
      'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
      'account_id': '123456', # VWO Account ID
      'batch_event_data': {
        'events_per_request': 60,  # Send up to 100 events per request
        'request_time_interval': 100, # Flush events every 60 seconds
        'flush_callback': event_flush_callback
      }
  }

  vwo_client = init(options)
  ```

  - You can also manually flush events using the `flush_events()` method:
  ```python
  vwo_client.flush_events()
  ```

## [1.8.0] - 2025-04-22

### Added

- Added support to add single `transport` or multiple transport using key `transports`. The transport parameter allows you to implement custom logging behavior by providing your own logging functions.

  ```python
  from vwo import init

  class CustomTransport:
    def __init__(self, config):
        self.level = config.get('level', "ERROR")
        self.config = config

    def log(self, level, message):
        # your custom implementation here

  options = {
      'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
      'account_id': '123456', # VWO Account ID
      'logger' {
        'transport': CustomTransport({'level': 'INFO'})
      }
  }

  vwo_client = init(options)
  ```

- For multiple transports you can use the `transports` parameter. For example:
  ```python
  from vwo import init

  class CustomTransportForInfo:
      def __init__(self, config):
          self.level = config.get('level', "INFO")
          self.config = config

      def log(self, level, message):
          # your custom implementation here

  class CustomTransportForError:
      def __init__(self, config):
          self.level = config.get('level', "ERROR")
          self.config = config

      def log(self, level, message):
          # your custom implementation here

  options = {
      'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
      'account_id': '123456', # VWO Account ID
      'logger' {
          'transports': [
              CustomTransportForInfo({'level': 'INFO'}),
              CustomTransportForError({'level': 'ERROR'})
          ]
      }
  }

  vwo_client = init(options)
  ```

## [1.7.0] - 2025-04-11

### Added

- Added support for polling intervals to periodically fetch and update settings:
  - If `poll_interval` is set in options (must be >= 1000 milliseconds), that interval will be used
  - If `poll_interval` is configured in VWO application settings, that will be used
  - If neither is set, defaults to 10 minute polling interval

## [1.6.0] - 2025-04-04

### Added

- Added support for sending multiple attributes at once using `set_attribute` method by passing a dictionary of key-value pairs to update user attributes in a single API call.

## [1.5.0] - 2025-03-12

### Added

- Added support for sending error logs to VWO server for better debugging.

## [1.4.0] - 2024-11-22

### Added

- added support to use salt for bucketing if provided in the rule.

## [1.3.0] - 2024-11-22

### Added

- added new method `update_settings` to update settings on the vwo client instance.

## [1.2.0] - 2024-09-25

### Added

- Added support for Personalise rules within `Mutually Exclusive Groups`.

## [1.1.0] - 2024-08-29

### Fixed

- Fix: Check for None values in `user_agent` and `ip_address` when sending impressions to VWO.

## [1.0.0] - 2024-06-20

### Added

- First release of VWO Feature Management and Experimentation capabilities

  ```python
  from vwo import init

  options = {
      'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
      'account_id': '123456' # VWO Account ID
  }

  vwo_client = init(options)

  # set user context
  user_context = {'id': 'unique_user_id'}
  # returns a flag object
  get_flag = vwo_client.get_flag('feature_key', user_context)
  # check if flag is enabled
  is_enabled = get_flag.is_enabled()
  # get varible
  int_var = get_flag.get_variable('int_variable_key', 'default_value')

  # track event
  vwo_client.track_event('event_name', user_context, event_properties)

  # set attribute
  vwo_client.set_attribute('attribute_key', 'attribute_value', user_context)
  ```

- **Storage**

  ```python
  from vwo.packages.storage.connector import StorageConnector
  class UserStorage(StorageConnector):
      def get(self, key: str, user_id: str):
          return client_db.get(f"{key}_{user_id}")

      def set(self, value: dict):
          key = f"{value.get('featureKey')}_{value.get('userId')}"
          client_db[key] = {
              'rolloutKey': value.get('rolloutKey'),
              'rolloutVariationId': value.get('rolloutVariationId'),
              'rolloutId': value.get('rolloutId'),
              'experimentKey': value.get('experimentKey'),
              'experimentVariationId': value.get('experimentVariationId'),
              'experimentId': value.get('experimentId'),
          }
          return True

  options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '123456', # VWO Account ID
    'storage': UserStorage()
  }

  vwo_client = init(options)
  ```

- **Log messages**

  ```python
  options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '123456', # VWO Account ID
    'logger': {
      'level': 'DEBUG',
      'prefix': 'VWO-FME-PYTHON-SDK'
    }
  }

  vwo_client = init(options)
  ```

- **Polling support**

 ```python
  options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '123456', # VWO Account ID
    'poll_interval': 5000 # in milliseconds
  }

  vwo_client = init(options)
  ```
