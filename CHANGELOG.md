# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
          key = f"{value.get('featureKey')}_{value.get('user')}"
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

