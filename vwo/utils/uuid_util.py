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


import uuid


def get_random_uuid(sdk_key: str) -> str:
    """
    Generates a random UUID based on an API key.

    :param sdk_key: The API key used to generate a namespace for the UUID.
    :return: A random UUID string.
    """
    # Generate a namespace based on the API key using DNS namespace
    namespace = uuid.uuid5(uuid.NAMESPACE_DNS, sdk_key)
    # Generate a random UUID using the namespace derived from the API key
    random_uuid = uuid.uuid5(namespace, str(uuid.uuid4()))

    return str(random_uuid)


def get_uuid(user_id: str, account_id: str) -> str:
    """
    Generates a UUID for a user based on their userId and accountId.

    :param user_id: The user's ID.
    :param account_id: The account ID associated with the user.
    :return: A UUID string formatted without dashes and in uppercase.
    """
    VWO_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://vwo.com")
    # Generate a namespace UUID based on the accountId
    user_id_namespace = generate_uuid(str(account_id), VWO_NAMESPACE)
    # Generate a UUID based on the userId and the previously generated namespace
    uuid_for_user_id_account_id = generate_uuid(user_id, uuid.UUID(user_id_namespace))
    if uuid_for_user_id_account_id:
        # Remove all dashes from the UUID and convert it to uppercase
        desired_uuid = uuid_for_user_id_account_id.replace("-", "").upper()
        return desired_uuid
    return None


def generate_uuid(name: str, namespace: uuid.UUID) -> str:
    """
    Helper function to generate a UUID v5 based on a name and a namespace.

    :param name: The name from which to generate the UUID.
    :param namespace: The namespace used to generate the UUID.
    :return: A UUID string.
    """
    # Check for valid input to prevent errors
    if not name or not namespace:
        return None

    generated_uuid = uuid.uuid5(namespace, name)
    return str(generated_uuid)
