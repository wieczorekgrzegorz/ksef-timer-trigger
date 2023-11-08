"""Unit tests for modules.send_msg_to_queue.py"""
import datetime
import unittest
from unittest.mock import patch, MagicMock

from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSender

import context  # pylint: disable=import-error
from modules import send_msg_to_queue


class TestGetIterationInt(context.BaseTestCase):
    """Tests for get_iteration_int function."""

    def test_double_quotation_mark(self) -> None:
        """Tests handling double quotation marks used in argument passed to message_json."""
        test_message = '{"NIP": "1111111111", "iteration": 1, "reason": null, "status": true}'
        expected_outcome = 1

        self.assertEqual(
            first=send_msg_to_queue.get_iteration_int(message_json=test_message),
            second=expected_outcome,
        )

    def test_single_quotation_mark(self) -> None:
        """Tests handling single quotation marks used in argument passed to message_json."""
        test_message = "{'NIP': '1111111111', 'iteration': 1, 'reason': None, 'status': True}"
        expected_outcome = 1

        self.assertEqual(
            first=send_msg_to_queue.get_iteration_int(message_json=test_message),
            second=expected_outcome,
        )

    def test_invalid_input(self) -> None:
        """Tests raising ValueError when invalid input is passed to message_json"""
        test_message = "{'NIP': '1111111111', 'reason': None, 'status': True}"

        self.assertRaises(
            ValueError,
            send_msg_to_queue.get_iteration_int,
            test_message,
        )


class TestSetupServiceBusClient(context.BaseTestCase):
    """Tests for setup_servicebus_client function."""

    @patch("modules.send_msg_to_queue.ServiceBusClient")
    def test_setup_servicebus_client(self, mock_servicebus_client) -> None:
        """Tests whether ServiceBusClient is set up with correct arguments."""
        mock_servicebus_client.from_connection_string = MagicMock()
        servicebus_conn_str = "mock_conn_str"
        send_msg_to_queue.setup_servicebus_client(servicebus_conn_str=servicebus_conn_str)

        mock_servicebus_client.from_connection_string.assert_called_once_with(
            conn_str=servicebus_conn_str, logging_enable=True
        )

    @patch("modules.send_msg_to_queue.ServiceBusClient")
    def test_setup_servicebus_client_return_type(self, mock_servicebus_client) -> None:
        """Tests whether ServiceBusClient returns object of ServiceBusClient type."""
        mock_servicebus_client_instance = MagicMock(spec=ServiceBusClient)
        mock_servicebus_client.from_connection_string = MagicMock(return_value=mock_servicebus_client_instance)
        servicebus_conn_str = "mock_conn_str"

        result = send_msg_to_queue.setup_servicebus_client(servicebus_conn_str=servicebus_conn_str)

        self.assertIsInstance(obj=result, cls=ServiceBusClient)


class TestSetupServiceBusSender(context.BaseTestCase):
    """Tests for setup_servicebus_sender function."""

    @patch("modules.send_msg_to_queue.ServiceBusClient")
    def test_setup_servicebus_sender(self, mock_servicebus_client) -> None:
        """Tests whether ServiceBusSender is set up with correct arguments."""
        mock_servicebus_sender = MagicMock()
        mock_servicebus_client.get_queue_sender = MagicMock(return_value=mock_servicebus_sender)
        queue_name = "mock_queue_name"
        send_msg_to_queue.setup_servicebus_sender(servicebus_client=mock_servicebus_client, queue_name=queue_name)

        mock_servicebus_client.get_queue_sender.assert_called_once_with(queue_name=queue_name)

    @patch("modules.send_msg_to_queue.ServiceBusClient")
    def test_setup_servicebus_sender_return_type(self, mock_servicebus_client) -> None:
        """Tests whether setup_servicebus_sender returns object of ServiceBusSender type."""
        mock_servicebus_sender = MagicMock(spec=ServiceBusSender)
        mock_servicebus_client.get_queue_sender = MagicMock(return_value=mock_servicebus_sender)
        queue_name = "mock_queue_name"

        result = send_msg_to_queue.setup_servicebus_sender(
            servicebus_client=mock_servicebus_client, queue_name=queue_name
        )

        self.assertIsInstance(obj=result, cls=ServiceBusSender)


class TestCreateServiceBusMessage(context.BaseTestCase):
    """Tests for create_servicebus_message function."""

    @patch("modules.send_msg_to_queue.ServiceBusMessage")
    def test_create_servicebus_message(self, mock_servicebus_message) -> None:
        """Tests whether ServiceBusMessage is created with correct arguments."""
        message_json = '{"key": "value"}'
        send_msg_to_queue.create_servicebus_message(message_json=message_json)

        mock_servicebus_message.assert_called_once_with(body=message_json)

    @patch("modules.send_msg_to_queue.ServiceBusMessage")
    def test_create_servicebus_message_return_type(self, mock_servicebus_message) -> None:
        """Tests whether create_servicebus_message returns object of ServiceBusMessage type."""
        mock_servicebus_message_instance = MagicMock(spec=ServiceBusMessage)
        mock_servicebus_message.return_value = mock_servicebus_message_instance
        message_json = '{"key": "value"}'

        result = send_msg_to_queue.create_servicebus_message(message_json=message_json)

        self.assertIsInstance(obj=result, cls=ServiceBusMessage)


class TestCalculateDelayMinutes(context.BaseTestCase):
    """Tests for calculate_delay_minutes function."""

    def test_calculate_delay_minutes(self) -> None:
        """Tests whether calculate_delay_minutes returns correct result."""
        iteration = 2
        multiplier = 3
        expected_result = 6.0

        result = send_msg_to_queue.calculate_delay_minutes(iteration=iteration, multiplier=multiplier)

        self.assertEqual(first=result, second=expected_result)

    def test_calculate_delay_minutes_return_type(self) -> None:
        """Tests whether calculate_delay_minutes returns object of int type."""
        iteration = 2
        multiplier = 3

        result = send_msg_to_queue.calculate_delay_minutes(iteration=iteration, multiplier=multiplier)

        self.assertIsInstance(obj=result, cls=int)


class TestSetupMessageDelay(context.BaseTestCase):
    """Tests for setup_message_delay function."""

    @patch("modules.send_msg_to_queue.datetime")
    def test_setup_message_delay(self, mock_datetime) -> None:
        """Tests whether setup_message_delay returns correct result."""
        mock_datetime.utcnow.return_value = datetime.datetime(2022, 1, 1, 0, 0, 0)
        delay_minutes = 60
        expected_result = datetime.datetime(2022, 1, 1, 1, 0, 0)

        result = send_msg_to_queue.setup_message_delay(delay_minutes=delay_minutes)

        self.assertEqual(first=result, second=expected_result)

    @patch("modules.send_msg_to_queue.datetime")
    def test_setup_message_delay_return_type(self, mock_datetime) -> None:
        """Tests whether setup_message_delay returns object of datetime type."""
        mock_datetime.utcnow.return_value = datetime.datetime(2022, 1, 1, 0, 0, 0)
        delay_minutes = 60

        result = send_msg_to_queue.setup_message_delay(delay_minutes=delay_minutes)

        self.assertIsInstance(obj=result, cls=datetime.datetime)


class TestSendScheduledMessage(context.BaseTestCase):  # pylint: disable=too-few-public-methods
    """Tests for send_scheduled_message function."""

    @patch("modules.send_msg_to_queue.ServiceBusSender")
    def test_send_scheduled_message(self, mock_servicebus_sender) -> None:
        """Tests whether send_scheduled_message calls schedule_messages with correct arguments."""
        mock_servicebus_sender_instance = MagicMock(spec=ServiceBusSender)
        mock_servicebus_sender_instance.schedule_messages = MagicMock()
        mock_servicebus_message = MagicMock(spec=ServiceBusMessage)
        scheduled_time_utc = datetime.datetime.utcnow()
        timeout = 60

        send_msg_to_queue.send_scheduled_message(
            sender=mock_servicebus_sender_instance,
            message=mock_servicebus_message,
            scheduled_time_utc=scheduled_time_utc,
            timeout=timeout,
        )

        mock_servicebus_sender_instance.schedule_messages.assert_called_once_with(
            messages=mock_servicebus_message, schedule_time_utc=scheduled_time_utc, timeout=timeout
        )


class TestMain(context.BaseTestCase):  # pylint: disable=too-few-public-methods
    """Tests for main function."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        """Set up common test variables and mocks."""
        self.servicebus_conn_str = "Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=test"
        self.queue_name = "test_queue"
        self.message_json = '{"iteration": 1}'
        self.timeout = 120.0
        self.delay_multiplier = 10

        self.mock_servicebus_client_instance = MagicMock(spec=ServiceBusClient)
        self.mock_servicebus_sender_instance = MagicMock(spec=ServiceBusSender)
        self.mock_servicebus_message_instance = MagicMock(spec=ServiceBusMessage)

        self.iteration = 1
        self.delay_minutes = 10.0
        self.scheduled_time_utc = datetime.datetime.utcnow()

    @patch("modules.send_msg_to_queue.setup_servicebus_client")
    @patch("modules.send_msg_to_queue.setup_servicebus_sender")
    @patch("modules.send_msg_to_queue.create_servicebus_message")
    @patch("modules.send_msg_to_queue.get_iteration_int")
    @patch("modules.send_msg_to_queue.calculate_delay_minutes")
    @patch("modules.send_msg_to_queue.setup_message_delay")
    @patch("modules.send_msg_to_queue.send_scheduled_message")
    def test_main(  # pylint: disable=too-many-arguments
        self,
        mock_send_scheduled_message,
        mock_setup_message_delay,
        mock_calculate_delay_minutes,
        mock_get_iteration_int,
        mock_create_servicebus_message,
        mock_setup_servicebus_sender,
        mock_setup_servicebus_client,
    ) -> None:
        """Tests whether main function calls all necessary functions with correct arguments."""

        mock_setup_servicebus_client.return_value = self.mock_servicebus_client_instance
        mock_setup_servicebus_sender.return_value = self.mock_servicebus_sender_instance
        mock_create_servicebus_message.return_value = self.mock_servicebus_message_instance
        mock_get_iteration_int.return_value = self.iteration
        mock_calculate_delay_minutes.return_value = self.delay_minutes
        mock_setup_message_delay.return_value = self.scheduled_time_utc

        send_msg_to_queue.main(
            servicebus_conn_str=self.servicebus_conn_str,
            queue_name=self.queue_name,
            message_json=self.message_json,
            timeout=self.timeout,
            delay_multiplier=self.delay_multiplier,
        )

        mock_setup_servicebus_client.assert_called_once_with(servicebus_conn_str=self.servicebus_conn_str)
        mock_setup_servicebus_sender.assert_called_once_with(
            servicebus_client=self.mock_servicebus_client_instance, queue_name=self.queue_name
        )
        mock_create_servicebus_message.assert_called_once_with(message_json=self.message_json)
        mock_get_iteration_int.assert_called_once_with(message_json=self.message_json)
        mock_calculate_delay_minutes.assert_called_once_with(iteration=self.iteration, multiplier=self.delay_multiplier)
        mock_setup_message_delay.assert_called_once_with(delay_minutes=self.delay_minutes)
        mock_send_scheduled_message.assert_called_once_with(
            sender=self.mock_servicebus_sender_instance,
            message=self.mock_servicebus_message_instance,
            scheduled_time_utc=self.scheduled_time_utc,
            timeout=self.timeout,
        )


if __name__ == "__main__":
    unittest.main()
