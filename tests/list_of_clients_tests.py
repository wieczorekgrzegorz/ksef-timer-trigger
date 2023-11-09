"""Tests for modules.list_of_clients.py module."""
import datetime
import json
import unittest
from unittest.mock import patch, Mock

import context  # pylint: disable=import-error, wrong-import-position
from modules import list_of_clients


class TestQueryClientsConfigTable(context.BaseTestCase):  # pylint: disable=too-few-public-methods
    """Tests for query_clients_config_table function."""

    @patch("requests.post")
    def test_query_clients_config_table(self, mock_post) -> None:
        """Tests if the function returns the correct response from the storage_table_connector function."""
        mock_response = Mock()
        mock_response.content = b'{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response
        expected_result = {"key": "value"}

        result = list_of_clients.query_clients_config_table(
            storage_acc_access_point="https://test.storage.acc",
            timeout=120,
            headers={"Content-Type": "application/json"},
            request_body='{"query": "SELECT * FROM ClientConfig"}',
            api_key="test_api_key",
        )

        self.assertEqual(first=result, second=expected_result)
        mock_post.assert_called_with(
            url="https://test.storage.acc",
            timeout=120,
            headers={"Content-Type": "application/json"},
            data='{"query": "SELECT * FROM ClientConfig"}',
            params={"code": "test_api_key"},
        )

    @patch("requests.post")
    def test_query_clients_config_table_json_decode_error(self, mock_post) -> None:
        """Tests if the function raises an exception when the response from the storage_table_connector function"""
        mock_response = Mock()
        mock_response.content = b"not json"
        error_msg = "Invalid json"
        mock_response.json.side_effect = json.JSONDecodeError(msg=error_msg, doc="not json", pos=0)
        mock_post.return_value = mock_response

        with self.assertRaises(expected_exception=json.JSONDecodeError) as cm:
            list_of_clients.query_clients_config_table(
                storage_acc_access_point="https://test.storage.acc",
                timeout=120,
                headers={"Content-Type": "application/json"},
                request_body='{"query": "SELECT * FROM ClientConfig"}',
                api_key="test_api_key",
            )
            self.assertEqual(first=cm.exception.msg, second=error_msg)


class TestValidateResponseFromStorageTableConnector(context.BaseTestCase):
    """Tests for validate_response_from_storage_table_connector function."""

    def test_validate_response_from_storage_table_connector_valid(self) -> None:
        """Tests if the function validates a valid response from the storage_table_connector function."""
        response_json = {
            "error": None,
            "query_result": ["record1", "record2"],
        }

        # Tested function called with this response_json should not raise any exceptions.
        list_of_clients.validate_response_from_storage_table_connector(response_json=response_json)

    def test_validate_response_from_storage_table_connector_missing_key(self) -> None:
        """Tests if the function raises an exception when a mandatory key is missing in the response from the
        storage_table_connector function."""
        response_json = {
            "error": None,
        }
        expected_err_msg = "Key query_result missing in response from storage_table_connector."
        with self.assertRaises(expected_exception=RuntimeError) as cm:
            list_of_clients.validate_response_from_storage_table_connector(response_json=response_json)
        self.assertEqual(first=str(object=cm.exception), second=expected_err_msg)

    def test_validate_response_from_storage_table_connector_error(self) -> None:
        """Tests if the function raises an exception when the response from the storage_table_connector function."""
        response_json = {
            "error": {"error": "SomeError", "message": "Some error occurred"},
            "query_result": ["record1", "record2"],
        }
        expected_err_msg = "SomeError: Some error occurred."

        with self.assertRaises(expected_exception=RuntimeError) as cm:
            list_of_clients.validate_response_from_storage_table_connector(response_json=response_json)
        self.assertEqual(first=str(object=cm.exception), second=expected_err_msg)

    def test_validate_response_from_storage_table_connector_empty_query_result(self) -> None:
        """Tests if the function raises an exception when the query_result is empty in the response from the
        storage_table_connector function."""
        response_json = {
            "error": None,
            "query_result": [],
        }
        expected_err_msg = "No records found in ClientsConfig table."

        with self.assertRaises(expected_exception=RuntimeError) as cm:
            list_of_clients.validate_response_from_storage_table_connector(response_json=response_json)
        self.assertEqual(first=str(object=cm.exception), second=expected_err_msg)


class TestCheckedRecently(context.BaseTestCase):
    """Tests for checked_recently function."""

    def test_checked_recently_valid(self) -> None:
        """Tests if the function correctly checks if a datetime string is within a target timedelta."""
        datetime_string = (
            datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=1)
        ).isoformat()
        target_timedelta = datetime.timedelta(hours=2)
        self.assertTrue(
            expr=list_of_clients.checked_recently(datetime_string=datetime_string, target_timedelta=target_timedelta)
        )

    def test_checked_recently_outside_timedelta(self) -> None:
        """Tests if the function correctly checks if a datetime string is outside a target timedelta."""
        datetime_string = (
            datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=3)
        ).isoformat()
        target_timedelta = datetime.timedelta(hours=2)
        self.assertFalse(
            expr=list_of_clients.checked_recently(datetime_string=datetime_string, target_timedelta=target_timedelta)
        )

    def test_checked_recently_none_datetime_string(self) -> None:
        """Tests if the function correctly handles a None datetime string."""
        datetime_string = None
        target_timedelta = datetime.timedelta(hours=2)
        self.assertFalse(
            expr=list_of_clients.checked_recently(datetime_string=datetime_string, target_timedelta=target_timedelta)
        )

    def test_checked_recently_null_datetime_string(self) -> None:
        """Tests if the function correctly handles a null datetime string."""
        datetime_string = "null"
        target_timedelta = datetime.timedelta(hours=2)
        self.assertFalse(
            expr=list_of_clients.checked_recently(datetime_string=datetime_string, target_timedelta=target_timedelta)
        )

    def test_checked_recently_invalid_datetime_string(self) -> None:
        """Tests if the function correctly handles an invalid datetime string."""
        datetime_string = "invalid"
        target_timedelta = datetime.timedelta(hours=2)

        expected_err_msg = f"Invalid isoformat string: '{datetime_string}'"

        with self.assertRaises(expected_exception=ValueError) as cm:
            list_of_clients.checked_recently(
                datetime_string=datetime_string, target_timedelta=target_timedelta  # type: ignore
            )
        self.assertEqual(first=str(object=cm.exception), second=expected_err_msg)

    def test_checked_recently_invalid_target_timedelta(self) -> None:
        """Tests if the function correctly raises a TypeError when the target_timedelta is not a timedelta."""
        datetime_string = (
            datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=1)
        ).isoformat()
        target_timedelta = "invalid"

        expected_err_msg = "'<' not supported between instances of 'datetime.timedelta' and 'str'"

        with self.assertRaises(expected_exception=TypeError) as cm:
            list_of_clients.checked_recently(
                datetime_string=datetime_string, target_timedelta=target_timedelta  # type: ignore
            )
        self.assertEqual(first=str(object=cm.exception), second=expected_err_msg)


class TestCreateListOfMessages(context.BaseTestCase):
    """Tests for create_list_of_messages function."""

    def test_create_list_of_messages_valid(self) -> None:
        """Tests if the function correctly creates a list of messages."""
        query_result = [
            {
                "PartitionKey": "1234567890",
                "last_successfull_download_run": (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat(),
                "penultimate_successfull_download_run": (
                    datetime.datetime.utcnow() - datetime.timedelta(hours=6)
                ).isoformat(),
            }
        ]
        re_run_interval = datetime.timedelta(hours=2)
        func_checked_recently = Mock(return_value=False)
        expected_result = [
            json.dumps(
                obj={
                    "NIP": "1234567890",
                    "last_successful_downloads": [
                        query_result[0]["last_successfull_download_run"],
                        query_result[0]["penultimate_successfull_download_run"],
                    ],
                    "iteration": 0,
                    "query_elem_ref_no": None,
                    "part_elem_ref_no": None,
                }
            )
        ]

        result = list_of_clients.create_list_of_messages(
            query_result=query_result, re_run_interval=re_run_interval, func_checked_recently=func_checked_recently
        )

        self.assertEqual(
            first=result,
            second=expected_result,
        )

    def test_create_list_of_messages_empty(self) -> None:
        """Tests if the function correctly handles an empty query result."""
        query_result = []
        re_run_interval = datetime.timedelta(hours=2)
        func_checked_recently = Mock(return_value=False)
        with self.assertRaises(expected_exception=SystemExit):
            list_of_clients.create_list_of_messages(
                query_result=query_result, re_run_interval=re_run_interval, func_checked_recently=func_checked_recently
            )

    def test_create_list_of_messages_all_recent(self) -> None:
        """Tests if the function correctly handles a query result where all items were checked recently."""
        query_result = [
            {
                "PartitionKey": "1234567890",
                "last_successfull_download_run": (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat(),
                "penultimate_successfull_download_run": (
                    datetime.datetime.utcnow() - datetime.timedelta(hours=2)
                ).isoformat(),
            }
        ]
        re_run_interval = datetime.timedelta(hours=2)
        func_checked_recently = Mock(return_value=True)
        with self.assertRaises(expected_exception=SystemExit):
            list_of_clients.create_list_of_messages(
                query_result=query_result, re_run_interval=re_run_interval, func_checked_recently=func_checked_recently
            )


class TestGet(context.BaseTestCase):  # pylint: disable=too-few-public-methods
    """No unittests to be had, as function get only calls consecutive functions that are already tested."""


if __name__ == "__main__":
    unittest.main()
