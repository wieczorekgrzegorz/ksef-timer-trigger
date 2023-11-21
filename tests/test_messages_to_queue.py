"""Unit tests for modules.messages_to_queue.py"""
import unittest
from unittest.mock import create_autospec, Mock

from azure.servicebus import ServiceBusMessage, ServiceBusMessageBatch

# freezegun is necessary because the get_scheduled_enqueue_time_utc function uses\
# datetime.datetime.utcnow() to get the current time

from tests import context  # pylint: disable=import-error
from modules import messages_to_queue


class TestBuildListOfServiceBusMessages(context.BaseTestCase):
    """Tests for build_list_of_service_bus_messages function."""

    def test_build_list_of_service_bus_messages(self) -> None:
        """Tests if the function returns a list of ServiceBusMessages with correct parameters."""
        list_of_messages = ["message1", "message2"]

        result = messages_to_queue.build_list_of_service_bus_messages(list_of_messages=list_of_messages)

        self.assertEqual(first=len(result), second=2)

    def test_function_returns_list_of_service_bus_messages(self) -> None:
        """Tests if the function returns a list of ServiceBusMessages with correct parameters."""
        list_of_messages = ["message1", "message2"]

        result = messages_to_queue.build_list_of_service_bus_messages(list_of_messages=list_of_messages)

        self.assertIsInstance(obj=result, cls=list)
        self.assertIsInstance(obj=result[0], cls=ServiceBusMessage)
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
