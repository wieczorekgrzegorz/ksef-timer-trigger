"""Tests for config module."""
import os
import unittest
from unittest.mock import patch

import context  # pylint: disable=import-error, wrong-import-position


class TestConfig(context.BaseTestCase):
    """Tests for config module."""

    @patch.dict(
        os.environ,
        {
            "STORAGE_TABLE_CONNECTOR_ACCESS_POINT": "mock_access_point",
            "STORAGE_TABLE_CONNECTOR_API_KEY": "mock_api_key",
            "SERVICEBUS_CONNECTION_STRING": "mock_connection_string",
            "SERVICEBUS_QUEUE_NIP_TO_CHECK": "mock_queue",
            "SERVICEBUS_APP_SETTING_NAME": "SERVICEBUS_CONNECTION_STRING",
        },
    )
    def test_environment_variables(self) -> None:
        """Tests whether environment variables are correctly set."""
        # pylint: disable=import-outside-toplevel, no-name-in-module, E0401:import-error
        # importing in this place intentionally to mock environment variables
        from modules.utilities import config

        self.assertEqual(first=config.STORAGE_TABLE_CONNECTOR_ACCESS_POINT, second="mock_access_point")
        self.assertEqual(first=config.STORAGE_TABLE_CONNECTOR_API_KEY, second="mock_api_key")
        self.assertEqual(first=config.SERVICEBUS_CONNECTION_STRING, second="mock_connection_string")
        self.assertEqual(first=config.QUEUE_INTERNAL, second="mock_queue")
        self.assertEqual(first=config.SERVICEBUS_APP_SETTING_NAME, second="SERVICEBUS_CONNECTION_STRING")


if __name__ == "__main__":
    unittest.main()
