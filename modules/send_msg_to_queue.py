"""Sends a message back to the queue with a scheduled delay (default=120s) set up."""
from datetime import datetime, timedelta
import ast
import json
import logging

from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSender

log = logging.getLogger(name="log." + __name__)


def setup_servicebus_client(servicebus_conn_str: str) -> ServiceBusClient:
    """Sets up a ServiceBusClient.

    Parameters:
        servicebus_conn_str (str): Service Bus connection string.

    Returns:
        servicebus_client (ServiceBusClient): ServiceBusClient set up successfully.
    """

    log.debug(msg="Setting up ServiceBusClient.")
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_conn_str, logging_enable=True)
    log.debug(msg=f"ServiceBusClient {servicebus_client} set up successfully.")
    return servicebus_client


def setup_servicebus_sender(servicebus_client: ServiceBusClient, queue_name: str) -> ServiceBusSender:
    """Sets up a ServiceBusSender.

    Parameters:
        servicebus_client (ServiceBusClient): ServiceBusClient.
        queue_name (str): Queue name.

    Returns:
        sender (ServiceBusSender): ServiceBusSender set up successfully.
    """

    log.debug(msg="Setting up ServiceBusSender.")
    sender = servicebus_client.get_queue_sender(queue_name=queue_name)
    log.debug(msg=f"ServiceBusSender {sender} set up successfully.")
    return sender


def create_servicebus_message(message_json: str) -> ServiceBusMessage:
    """Creates a ServiceBusMessage.

    Parameters:
        message_json (str).

    Returns:
        service_bus_message (ServiceBusMessage).
    """

    log.debug(msg="Creating ServiceBusMessage.")
    service_bus_message = ServiceBusMessage(body=message_json)
    log.debug(msg="ServiceBusMessage created successfully.")
    return service_bus_message


def get_iteration_int(message_json: str) -> int:
    """Parses iteration int from message_json using json.loads.
    In case of ValueError, tries to parse using ast.literal_eval.

    Parameters:
        message_json (str): Message in json format.

    Returns:
        iteration_int (int)"""

    log.debug(msg="Getting iteration int.")

    try:
        iteration_int = json.loads(message_json)["iteration"]

    except ValueError:
        try:
            iteration_int = ast.literal_eval(node_or_string=message_json)["iteration"]
        except Exception as e:
            log.error(msg=f"Error: {e}")
            raise ValueError(e) from e

    log.debug(msg=f"Iteration int {iteration_int} received successfully.")
    return iteration_int


def calculate_delay_minutes(iteration: int, multiplier: int) -> int:
    """Calculates delay minutes.
    delay_minutes = iteration * multiplier"""
    log.debug(msg="Calculating delay minutes.")
    delay_minutes = iteration * multiplier
    log.debug(msg=f"Delay {delay_minutes} minutes calculated successfully.")
    return delay_minutes


def setup_message_delay(delay_minutes: int) -> datetime:
    """Sets up a message delay.

    Parameters:
        delay_hours (float): Delay in hours.
        delay_minutes (float): Delay in minutes.
        delay_seconds (float): Delay in seconds.

    Returns:
        scheduled_time_utc (datetime): Message delay set up successfully.
    """

    log.debug(msg="Setting up message delay.")
    scheduled_time_utc = datetime.utcnow() + timedelta(minutes=delay_minutes)
    log.debug(msg=f"Message delay set up successfully to {scheduled_time_utc}.")
    return scheduled_time_utc


def send_scheduled_message(
    sender: ServiceBusSender,
    message: ServiceBusMessage,
    scheduled_time_utc: datetime,
    timeout: float | None = None,
) -> None:
    """Sends a scheduled message.

    Parameters:
        sender (ServiceBusSender): ServiceBusSender.
        message (ServiceBusMessage): Message to be sent.
        scheduled_time_utc (datetime): Scheduled time in UTC.
        timeout (float | None): Timeout in seconds.

    Returns:
        None
    """

    log.debug(msg="Sending scheduled message.")
    sender.schedule_messages(messages=message, schedule_time_utc=scheduled_time_utc, timeout=timeout)
    log.debug(msg="Scheduled message sent successfully.")


def main(
    servicebus_conn_str: str,
    queue_name: str,
    message_json: str,
    timeout: float | None = 120,
    delay_multiplier: int = 10,
) -> None:
    """Sends a scheduled message to specified Service Bus Queue.
    Sets up a ServiceBusClient, a ServiceBusSender, a ServiceBusMessage and a delay for scheduled message.
    Delay (in minutes) for scheduled message is calculated as iteration (parsed from message_json) * delay_multiplier.

    Parameters:
        servicebus_conn_str (str): Service Bus connection string.
        queue_name (str): Queue name.
        message_json (str): Message in json format.
        delay_multiplier (int): Delay multiplier. Default=10.
        timeout (float | None): Timeout in seconds. Default=120s.

    Returns:
        None
    """
    log.debug(msg=f"Received a request to send message {message_json} to queue {queue_name}.")
    servicebus_client = setup_servicebus_client(servicebus_conn_str=servicebus_conn_str)

    with servicebus_client:
        sender = setup_servicebus_sender(servicebus_client=servicebus_client, queue_name=queue_name)

        message = create_servicebus_message(message_json=message_json)

        iteration = get_iteration_int(message_json=message_json)

        delay_minutes = calculate_delay_minutes(iteration=iteration, multiplier=delay_multiplier)

        scheduled_time_utc = setup_message_delay(
            delay_minutes=delay_minutes,
        )

        send_scheduled_message(
            sender=sender,
            message=message,
            scheduled_time_utc=scheduled_time_utc,
            timeout=timeout,
        )

    log.info(msg=f"Message {message} sent successfully.", stacklevel=2)
