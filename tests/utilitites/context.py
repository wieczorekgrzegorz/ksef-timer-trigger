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
sys.path.insert(0, str(path(__file__).parents[2]))

# # define global variables for tests
# # Reason: So every test uses same mock values for environment variables
# # Reason 2: tests would fail with KeyError("AZURE_COSMOSDB_CONNECTION_STRING")
# #           exception when importing function_app
# os.environ["AZURE_COSMOSDB_CONNECTION_STRING"] = "mock_connection_string"
# os.environ["DATABASE_ID"] = "mock_database_id"
# os.environ["CONTAINER_ID"] = "mock_container_id"


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
        patch("modules.send_msg_to_queue.log").start()
        patch("modules.timer_trigger.log").start()

    @classmethod
    def tearDownClass(cls) -> None:
        print("\nTESTS FINISHED")
        patch.stopall()

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass
