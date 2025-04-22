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


from murmurhash import mrmr
import math

SEED_VALUE = 1  # Seed value for the hash function


class DecisionMaker:

    def __init__(self):
        self.seed_value = SEED_VALUE

    def generate_bucket_value(
        self, hash_value: int, max_value: int, multiplier: int = 1
    ) -> int:
        """
        Generates a bucket value based on the hash value, maximum value, and an optional multiplier.

        :param hash_value: The hash value used for calculation.
        :param max_value: The maximum value for bucket scaling.
        :param multiplier: Optional multiplier to adjust the value.
        :return: The calculated bucket value.
        """
        # Calculate the ratio based on the hash value
        ratio = hash_value / (2**32)
        # Calculate the multiplied value
        multiplied_value = (max_value * ratio + 1) * multiplier
        # Round down to get the final value
        value = math.floor(multiplied_value)

        return value

    def get_bucket_value_for_user(self, hash_key: str, max_value: int = 100) -> int:
        """
        Gets the bucket value for a user based on the hash key and maximum value.

        :param hash_key: The hash key for the user.
        :param max_value: The maximum value for bucket scaling.
        :return: The calculated bucket value for the user.
        """
        hash_value = self.generate_hash_value(hash_key)  # Calculate the hash value
        bucket_value = self.generate_bucket_value(
            hash_value, max_value
        )  # Calculate the bucket value

        return bucket_value  # Return the calculated bucket value

    def calculate_bucket_value(
        self, string: str, multiplier: int = 1, max_value: int = 10000
    ) -> int:
        """
        Calculates the bucket value for a given string with optional multiplier and maximum value.

        :param string: The input string to calculate the bucket value for.
        :param multiplier: Optional multiplier to adjust the value.
        :param max_value: The maximum value for bucket scaling.
        :return: The calculated bucket value.
        """
        hash_value = self.generate_hash_value(
            string
        )  # Generate the hash value for the input string
        return self.generate_bucket_value(
            hash_value, max_value, multiplier
        )  # Generate and return the bucket value

    def generate_hash_value(self, hash_key: str) -> int:
        """
        Generates the hash value for a given hash key using MurmurHash v3.

        :param hash_key: The hash key for which the hash value is generated.
        :return: The generated hash value.
        """
        # Ensure the hash is treated as an unsigned 32-bit integer
        hash_value = mrmr.hash(hash_key, self.seed_value)
        return hash_value & 0xFFFFFFFF  # Convert to unsigned 32-bit integer
