# type: ignore # Pylance returns fake-negative import error. Imports here are used as context for unit tests.
# flake8: noqa: F401, F402 # imports in this file are used in other files
"""Context file for unit tests. 
Mocks environment variables and inserts main app folder to PATH.
Turns off logging for tested modules.
"""
import os
from pathlib import PurePath as path
import sys
import unittest
from unittest.mock import patch


# adding main app folder to PATH
sys.path.insert(0, str(path(__file__).parents[1]))


# Mock env variables
os.environ["STORAGE_TABLE_CONNECTOR_ACCESS_POINT"] = "https://test.storage.acc"
os.environ["STORAGE_TABLE_CONNECTOR_API_KEY"] = "test_api_key"


class BaseTestCase(unittest.TestCase):
    """
    A base test case class that sets up common functionality for all unit tests.

    This class handles the setup and teardown of resources common to all tests.
    It also sets up common mock objects and patches for logging.

    Attributes:
        mock_log: A mock object for the get_req_body.log module.
        mock_error_log: A mock object for the custom_error.log module.

    Methods:
        setUpClass: Class method called before running tests in an individual class.
        tearDownClass: Class method called after running all tests in an individual class.
        setUp: Instance method called before running each test method.
        tearDown: Instance method called after running each test method.
    """

    @classmethod
    def setUpClass(cls) -> None:
        print(f"\nRUNNING TESTS FOR: {cls.__name__}.")
        patch("modules.messages_to_queue.log").start()
        patch("modules.list_of_clients.log").start()

    @classmethod
    def tearDownClass(cls) -> None:
        print("\nTESTS FINISHED")
        patch.stopall()

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass
