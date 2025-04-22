# Copyright 2024-2025 Wingify Software Pvt. Ltd.
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


from typing import Any, Dict, Callable, List
import re
from datetime import datetime

# Define a generic dynamic type
dynamic = Any

# Define a function type for comparison
FunctionType = Callable[[dynamic], None]


def is_object(val: dynamic) -> bool:
    """Checks if a value is an object excluding arrays, functions, regexes, promises, and dates."""
    return isinstance(val, Dict)


def is_array(val: dynamic) -> bool:
    """Checks if a value is an array (List in Python)."""
    return isinstance(val, List)


def is_null(val: dynamic) -> bool:
    """Checks if a value is None (null in Python)."""
    return val is None


def is_undefined(val: dynamic) -> bool:
    """Checks if a value is None (undefined in Python)."""
    # In Python, 'undefined' is typically treated as None
    return val is None


def is_defined(val: dynamic) -> bool:
    """Checks if a value is defined, i.e., not None."""
    return val is not None


def is_number(val: dynamic) -> bool:
    """Checks if a value is a number, including NaN."""
    return isinstance(val, (int, float))


def is_string(val: dynamic) -> bool:
    """Checks if a value is a string."""
    return isinstance(val, str)


def is_boolean(val: dynamic) -> bool:
    """Checks if a value is a boolean."""
    return isinstance(val, bool)


def is_nan(val: dynamic) -> bool:
    """Checks if a value is NaN."""
    try:
        return isinstance(val, float) and val != val
    except TypeError:
        return False


def is_date(val: dynamic) -> bool:
    """Checks if a value is a Date object."""
    return isinstance(val, datetime)


def is_function(val: dynamic) -> bool:
    """Checks if a value is a function."""
    return callable(val)


def is_regex(val: dynamic) -> bool:
    """Checks if a value is a regular expression."""
    return isinstance(val, re.Pattern)


def is_promise(val: dynamic) -> bool:
    """Checks if a value is a Future object (closest to a Promise in Python)."""
    from concurrent.futures import Future

    return isinstance(val, Future)


def get_type(val: dynamic) -> str:
    """Determines the type of the given value using various type-checking utility functions."""
    if is_object(val):
        return "Object"
    elif is_array(val):
        return "Array"
    elif is_null(val):
        return "Null"
    elif is_undefined(val):
        return "Undefined"
    elif is_nan(val):
        return "NaN"
    elif is_number(val):
        return "Number"
    elif is_string(val):
        return "String"
    elif is_boolean(val):
        return "Boolean"
    elif is_date(val):
        return "Date"
    elif is_regex(val):
        return "Regex"
    elif is_function(val):
        return "Function"
    elif is_promise(val):
        return "Promise"
    else:
        return "Unknown Type"
