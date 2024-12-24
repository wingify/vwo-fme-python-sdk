## VWO Feature Management and Experimentation SDK for Python

[![PyPI version](https://badge.fury.io/py/vwo-fme-python-sdk.svg)](https://pypi.org/project/vwo-fme-python-sdk)
[![CI](https://github.com/wingify/vwo-fme-python-sdk/workflows/CI/badge.svg?branch=master)](https://github.com/wingify/vwo-fme-python-sdk/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/wingify/vwo-fme-python-sdk/branch/master/graph/badge.svg?token=)](https://codecov.io/gh/wingify/vwo-fme-python-sdk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

## Overview

The **VWO Feature Management and Experimentation SDK** (VWO FME Python SDK) enables python developers to integrate feature flagging and experimentation into their applications. This SDK provides full control over feature rollout, A/B testing, and event tracking, allowing teams to manage features dynamically and gain insights into user behavior.

## Requirements

* Works with Python: 3.6 onwards.

## Installation

It's recommended you use [virtualenv](https://virtualenv.pypa.io/en/latest/) to create isolated Python environments.

```bash
pip install vwo-fme-python-sdk
```

## Basic Usage Example

The following example demonstrates initializing the SDK with a VWO account ID and SDK key, setting a user context, checking if a feature flag is enabled, and tracking a custom event.
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

## Advanced Configuration Options

To customize the SDK further, additional parameters can be passed to the `init()` API. Here’s a table describing each option:

| **Parameter**                | **Description**                                                                                                                                             | **Required** | **Type** | **Example**                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | -------- | ------------------------------- |
| `account_id`                  | VWO Account ID for authentication.                                                                                                                          | Yes          | str   | `'123456'`                      |
| `sdk_key`                     | SDK key corresponding to the specific environment to initialize the VWO SDK Client. You can get this key from VWO Application.                              | Yes          | str   | `'32-alpha-numeric-sdk-key'`    |
| `poll_interval`               | Time interval for fetching updates from VWO servers (in milliseconds).                                                                                      | No           | int   | `60_000`                         |
| `gateway_service`             | Configuration for integrating VWO Gateway Service. Service.                                                                                   | No           | Dictionary   | see [Gateway](#gateway) section |
| `storage`                    | Custom storage connector for persisting user decisions and campaign data. data.                                                                                   | No           | Dictionary   | See [Storage](#storage) section |
| `logger`                     | Toggle log levels for more insights or for debugging purposes. You can also customize your own transport in order to have better control over log messages. | No           | Dictionary   | See [Logger](#logger) section   |
| `integrations`               | Callback function for integrating with third-party analytics services.                                                                                      | No           | Function | See [Integrations](#integrations) section |

### User Context

The `context` uniquely identifies users and is crucial for consistent feature rollouts. A typical `context` is a dictionary that includes an `id` key for identifying the user. It can also include other attributes that can be used for targeting and segmentation, such as `custom_variables`, `user_agent`, and `ip_address`.

#### Parameters Table

The following table explains all the parameters in the `context` dictionary:

| **Parameter**     | **Description**                                                            | **Required** | **Type** |
| ----------------- | -------------------------------------------------------------------------- | ------------ | -------- |
| `id`              | Unique identifier for the user.                                            | Yes          | str   |
| `custom_variables` | Custom attributes for targeting.                                           | No           | Dict |
| `user_agent`       | User agent string for identifying the user's browser and operating system. | No           | str   |
| `ip_address`       | IP address of the user.                                                    | No           | str   |

#### Example

```python
context = {
    'id': 'unique_user_id',
    'custom_variables': {
        'age': 25,
        'location': 'US'
    },
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'ip_address': '1.1.1.1'
}
```

### Basic Feature Flagging

Feature Flags serve as the foundation for all testing, personalization, and rollout rules within FME.
To implement a feature flag, first use the `get_flag()` method to retrieve the flag configuration.
The `get_flag()` method provides a simple way to check if a feature is enabled for a specific user and access its variables. It returns a `GetFlag` object that contains methods like `is_enabled()` for checking the feature's status and `get_variable()` for retrieving any associated variables.

| Parameter    | Description                                                      | Required | Type        |
| ------------ | ---------------------------------------------------------------- | -------- | ----------- |
| `feature_key` | Unique identifier of the feature flag                            | Yes      | str      |
| `context`    | Dictionary containing user identification and contextual information | Yes      | Dict  |

Example usage:

```python
feature_flag = vwo_client.get_flag("feature_key", context)
is_enabled = feature_flag.is_enabled()

if is_enabled:
  print("Feature is enabled!")

  # Get and use feature variable with type safety
  variable_value = feature_flag.get_variable('feature_variable', 'default_value')
  print("Variable value: " + variable_value)
else:
  print("Feature is not enabled!")
```

### Custom Event Tracking

Feature flags can be enhanced with connected metrics to track key performance indicators (KPIs) for your features. These metrics help measure the effectiveness of your testing rules by comparing control versus variation performance, and evaluate the impact of personalization and rollout campaigns. Use the `track_event()` method to track custom events like conversions, user interactions, and other important metrics:

| Parameter         | Description                                                            | Required | Type        |
| ----------------- | ---------------------------------------------------------------------- | -------- | ----------- |
| `event_name`       | Name of the event you want to track                                    | Yes      | str      |
| `context`         | Dictionary containing user identification and contextual information       | Yes      | Dict  |
| `event_properties` | Additional properties/metadata associated with the event               | No       | Dict |

Example usage:

```python
vwo_client.track_event('event_name', context, event_properties)
```

### Pushing Attributes

User attributes provide rich contextual information about users, enabling powerful personalization. The `set_attribute()` method in VWOClient provides a simple way to associate these attributes with users in VWO for advanced segmentation. The method accepts an attribute key, value, and dictionary containing the user information. Here's what you need to know about the method parameters:

| Parameter        | Description                                                            | Required | Type        |
| ---------------- | ---------------------------------------------------------------------- | -------- | ----------- |
| `attribute_key`   | The unique identifier/name of the attribute you want to set            | Yes      | str      |
| `attribute_value` | The value to be assigned to the attribute                              | Yes      | Any      |
| `context`        | Dictionary containing user identification and other contextual information | Yes      | Dict  |

Example usage:

```python
vwo_client.set_attribute('attribute_key', 'attribute_value', context)
```

### Polling Interval Adjustment

The `poll_interval` is an optional parameter that allows the SDK to automatically fetch and update settings from the VWO server at specified intervals. Setting this parameter ensures your application always uses the latest configuration.

```python
options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '123456', # VWO Account ID
    'poll_interval': 60000 # Set the poll interval to 60 seconds
}

vwo_client = init(options)
```

### Gateway

The VWO FME Gateway Service is an optional but powerful component that enhances VWO's Feature Management and Experimentation (FME) SDKs. It acts as a critical intermediary for pre-segmentation capabilities based on user location and user agent (UA). By deploying this service within your infrastructure, you benefit from minimal latency and strengthened security for all FME operations.

#### Why Use a Gateway?

The Gateway Service is required in the following scenarios:

- When using pre-segmentation features based on user location or user agent.
- For applications requiring advanced targeting capabilities.
- It's mandatory when using any thin-client SDK (e.g., Go).

#### How to Use the Gateway

The gateway can be customized by passing the `gateway_service` parameter in the `init` configuration.

```python
options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '123456', # VWO Account ID
    'gateway_service': {
        'url': 'http://custom.gateway.com'
    }
}
vwo_client = init(options)
```

### Storage

The SDK operates in a stateless mode by default, meaning each `get_flag` call triggers a fresh evaluation of the flag against the current user context.

To optimize performance and maintain consistency, you can implement a custom storage mechanism by passing a `storage` parameter during initialization. This allows you to persist feature flag decisions in your preferred database system (like Redis, MongoDB, or any other data store).

Key benefits of implementing storage:

- Improved performance by caching decisions
- Consistent user experience across sessions
- Reduced load on your application

The storage mechanism ensures that once a decision is made for a user, it remains consistent even if campaign settings are modified in the VWO Application. This is particularly useful for maintaining a stable user experience during A/B tests and feature rollouts.

```python
from vwo import StorageConnector
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

### Logger

VWO by default logs all `ERROR` level messages to your server console.
To gain more control over VWO's logging behaviour, you can use the `logger` parameter in the `init` configuration.

| **Parameter** | **Description**                        | **Required** | **Type** | **Default Value** |
| ------------- | -------------------------------------- | ------------ | -------- | ----------------- |
| `level`       | Log level to control verbosity of logs | Yes          | str   | `ERROR`           |
| `prefix`      | Custom prefix for log messages         | No           | str   | `VWO-SDK`             |

#### Example 1: Set log level to control verbosity of logs

```python
options = {
    'account_id': '123456', # VWO Account ID
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'logger': {
        'level': 'DEBUG'
    }
}
vwo_client = init(options)
```

#### Example 2: Add custom prefix to log messages for easier identification

```python
options = {
    'account_id': '123456', # VWO Account ID
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'logger': {
        'level': 'DEBUG',
        'prefix': 'CUSTOM LOG PREFIX'
    }
}
vwo_client = init(options)
```

### Integrations
VWO FME SDKs provide seamless integration with third-party tools like analytics platforms, monitoring services, customer data platforms (CDPs), and messaging systems. This is achieved through a simple yet powerful callback mechanism that receives VWO-specific properties and can forward them to any third-party tool of your choice.

```python
def callback(properties):
    # properties will contain all the required VWO specific information
    print(properties)

options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '12345', # VWO Account ID
    'integrations': {
        'callback': callback
    }
}
vwo_client = init(options)
```

## Local development

```bash
python setup.py develop
```

## Running Unit Tests

```bash
python setup.py test
```

## Authors

* [Abhishek Joshi](https://github.com/Abhi591)

### Version History

The version history tracks changes, improvements, and bug fixes in each version. For a full history, see the [CHANGELOG.md](https://github.com/wingify/vwo-fme-python-sdk/blob/master/CHANGELOG.md).

## Contributing

We welcome contributions to improve this SDK! Please read our [contributing guidelines](https://github.com/wingify/vwo-fme-python-sdk/blob/master/CONTRIBUTING.md) before submitting a PR.


## Code of Conduct

Our [Code of Conduct](https://github.com/wingify/vwo-fme-python-sdk/blob/master/CODE_OF_CONDUCT.md) outlines expectations for all contributors and maintainers.

## License

[Apache License, Version 2.0](https://github.com/wingify/vwo-fme-python-sdk/blob/master/LICENSE)

Copyright 2024 Wingify Software Pvt. Ltd.
