## VWO Feature Management and Experimentation SDK for Python

[![PyPI version](https://badge.fury.io/py/vwo-fme-python-sdk.svg)](https://pypi.org/project/vwo-fme-python-sdk)
[![CI](https://github.com/wingify/vwo-fme-python-sdk/workflows/CI/badge.svg?branch=master)](https://github.com/wingify/vwo-fme-python-sdk/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/wingify/vwo-fme-python-sdk/branch/master/graph/badge.svg?token=)](https://codecov.io/gh/wingify/vwo-fme-python-sdk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

This open source library allows you to A/B Test your Website at server-side.

## Requirements

* Works with Python: 3.6 onwards.

## Installation

It's recommended you use [virtualenv](https://virtualenv.pypa.io/en/latest/) to create isolated Python environments.

```bash
pip install vwo-fme-python-sdk
```

## Basic usage

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
from vwo import StorageConnector
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
from vwo import LogLevelEnum
options = {
    'sdk_key': '32-alpha-numeric-sdk-key', # SDK Key
    'account_id': '123456', # VWO Account ID
    'logger': {
        'level': LogLevelEnum.DEBUG,
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

## Changelog

Refer [CHANGELOG.md](https://github.com/wingify/vwo-fme-python-sdk/blob/master/CHANGELOG.md)

## Contributing

Please go through our [contributing guidelines](https://github.com/wingify/vwo-fme-python-sdk/blob/master/CONTRIBUTING.md)


## Code of Conduct

[Code of Conduct](https://github.com/wingify/vwo-fme-python-sdk/blob/master/CODE_OF_CONDUCT.md)

## License

[Apache License, Version 2.0](https://github.com/wingify/vwo-fme-python-sdk/blob/master/LICENSE)

Copyright 2024 Wingify Software Pvt. Ltd.
