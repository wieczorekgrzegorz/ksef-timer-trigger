"""Unit tests for modules.messages_to_queue.py"""
import datetime
import unittest
from unittest.mock import create_autospec, patch, MagicMock, Mock

from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSender, ServiceBusMessageBatch
from freezegun import freeze_time

# freezegun is necessary because the get_scheduled_enqueue_time_utc function uses\
# datetime.datetime.utcnow() to get the current time

import context  # pylint: disable=import-error
from modules import messages_to_queue


class TestGetScheduledEnqueueTimeUtc(context.BaseTestCase):
    """Tests for get_scheduled_enqueue_time_utc function."""

    @freeze_time(time_to_freeze="2022-01-01")
    def test_json_message(self) -> None:
        """Tests if the function returns the correct datetime.datetime object when parsing a json message."""
        message = '{"iteration": 2}'
        result = messages_to_queue.get_scheduled_enqueue_time_utc(message_str=message, delay_multiplier=2)
        expected_result = datetime.datetime(year=2022, month=1, day=1, hour=0, minute=4)
        self.assertEqual(first=result, second=expected_result)

    @freeze_time(time_to_freeze="2022-01-01")
    def test_literal_eval_message(self) -> None:
        """Tests if the function returns the correct datetime.datetime object when parsing a literal_eval message."""
        message = "{'iteration': 2}"
        result = messages_to_queue.get_scheduled_enqueue_time_utc(message_str=message, delay_multiplier=2)
        expected_result = datetime.datetime(year=2022, month=1, day=1, hour=0, minute=4)
        self.assertEqual(first=result, second=expected_result)

    @freeze_time(time_to_freeze="2022-01-01")
    def test_invalid_message(self) -> None:
        """Tests if the function raises an exception when parsing an invalid message.""" ""
        message = "invalid"
        with self.assertRaises(expected_exception=Exception):
            messages_to_queue.get_scheduled_enqueue_time_utc(message_str=message, delay_multiplier=2)


class TestBuildListOfServiceBusMessages(context.BaseTestCase):
    """Tests for build_list_of_service_bus_messages function."""

    def test_build_list_of_service_bus_messages(self) -> None:
        """Tests if the function returns a list of ServiceBusMessages with correct parameters."""
        mock_datetime = "2022-01-01 00:00:00"
        list_of_messages = ["message1", "message2"]

        mock_scheduled_enqueue_time_utc = Mock()
        mock_scheduled_enqueue_time_utc.return_value = mock_datetime

        result = messages_to_queue.build_list_of_service_bus_messages(
            list_of_messages=list_of_messages,
            delay_multiplier=2,
            func_get_scheduled_enqueue_time_utc=mock_scheduled_enqueue_time_utc,
        )

        self.assertEqual(first=len(result), second=2)
        mock_scheduled_enqueue_time_utc.assert_called_with(message_str=list_of_messages[-1], delay_multiplier=2)

    def test_function_returns_list_of_service_bus_messages(self) -> None:
        """Tests if the function returns a list of ServiceBusMessages with correct parameters."""
        mock_datetime = "2022-01-01 00:00:00"
        list_of_messages = ["message1", "message2"]

        mock_scheduled_enqueue_time_utc = Mock()
        mock_scheduled_enqueue_time_utc.return_value = mock_datetime

        result = messages_to_queue.build_list_of_service_bus_messages(
            list_of_messages=list_of_messages,
            delay_multiplier=2,
            func_get_scheduled_enqueue_time_utc=mock_scheduled_enqueue_time_utc,
        )

        self.assertIsInstance(obj=result, cls=list)
        self.assertIsInstance(obj=result[0], cls=ServiceBusMessage)
        self.assertEqual(first=result[0].scheduled_enqueue_time_utc, second=mock_datetime)
        self.assertEqual(first=str(object=result[0]), second=list_of_messages[0])


class TestBuildBatchMessage(context.BaseTestCase):
    """Tests for build_batch_message function."""

    def test_build_batch_message(self) -> None:
        """Tests if the function returns a batch message with correct parameters."""
        mock_message = create_autospec(spec=ServiceBusMessage)
        mock_message.body = "message1"
        list_of_service_bus_messages = [mock_message, mock_message]

        mock_batch = Mock()
        mock_sender = Mock()
        mock_sender.create_message_batch.return_value = mock_batch

        messages_to_queue.build_batch_message(
            list_of_service_bus_messages=list_of_service_bus_messages, sender=mock_sender
        )

        self.assertEqual(first=mock_batch.add_message.call_count, second=2)
        mock_batch.add_message.assert_called_with(message=mock_message)

    def test_function_returns_service_bus_sender(self) -> None:
        """Tests if the function returns a batch message with correct parameters."""
        mock_message = create_autospec(spec=ServiceBusMessage)
        mock_message.body = "message1"
        list_of_service_bus_messages = [mock_message, mock_message]

        mock_batch = Mock(spec=ServiceBusMessageBatch)
        mock_sender = Mock()
        mock_sender.create_message_batch.return_value = mock_batch

        result = messages_to_queue.build_batch_message(
            list_of_service_bus_messages=list_of_service_bus_messages, sender=mock_sender
        )

        self.assertIsInstance(obj=result, cls=ServiceBusMessageBatch)


if __name__ == "__main__":
    unittest.main()
