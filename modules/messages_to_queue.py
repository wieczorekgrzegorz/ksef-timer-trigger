"""Sends a message back to the queue with a scheduled delay (default=120s) set up."""
import ast
import datetime
import json
import logging
from typing import Callable


from azure.servicebus import ServiceBusClient, ServiceBusSender, ServiceBusMessage, ServiceBusMessageBatch

log = logging.getLogger(name="log." + __name__)


def get_scheduled_enqueue_time_utc(message_str: str, delay_multiplier: int) -> datetime.datetime:
    """Calculates scheduled enqueue time in UTC from message_str's iteration and delay_multiplier.\n
    Parses iteration int from message_str using json.loads.
    In case of ValueError, tries to parse using ast.literal_eval."""

    try:
        iteration = json.loads(s=message_str)["iteration"]
    except ValueError:
        iteration = ast.literal_eval(node_or_string=message_str)["iteration"]

    return datetime.datetime.utcnow() + datetime.timedelta(minutes=iteration * delay_multiplier)


def build_list_of_service_bus_messages(
    list_of_messages: list, delay_multiplier: int, timeout: int, func_get_scheduled_enqueue_time_utc: Callable
) -> list[ServiceBusMessage]:
    """Builds a list of ServiceBusMessages with scheduled enqueue time (a.k.a 'delay')."""

    list_of_service_bus_messages = []
    for message in list_of_messages:
        scheduled_enqueue_time_utc = func_get_scheduled_enqueue_time_utc(
            message_str=message, delay_multiplier=delay_multiplier
        )
        list_of_service_bus_messages.append(
            ServiceBusMessage(body=message, timeout=timeout, scheduled_enqueue_time_utc=scheduled_enqueue_time_utc)
        )
    log.info(msg=f"Built a list of {len(list_of_service_bus_messages)} messages.")

    return list_of_service_bus_messages


def build_batch_message(
    list_of_service_bus_messages: list[ServiceBusMessage], sender: ServiceBusSender
) -> ServiceBusMessageBatch:
    """Creates a batch message out of list_of_service_bus_messages."""
    batch_message = sender.create_message_batch()

    for service_bus_message in list_of_service_bus_messages:
        batch_message.add_message(message=service_bus_message)

        log.debug(msg=f"Added message to batch message. Message: {service_bus_message.body}.")

    log.info(msg=f"Built a batch message consisting of {len(list_of_service_bus_messages)} messages.")

    return batch_message


def send(
    servicebus_conn_str: str,
    queue_name: str,
    list_of_messages: list,
    timeout: int = 120,
    delay_multiplier: int = 2,
) -> None:
    """Sends a scheduled message to specified Service Bus Queue.
    Sets up a ServiceBusClient, a ServiceBusSender, a ServiceBusMessage and a delay for scheduled message.
    Delay (in minutes) for scheduled message is calculated as iteration (parsed from message_json) * delay_multiplier.

    Parameters:
        servicebus_conn_str (str): Service Bus connection string.
        queue_name (str): Queue name.
        message_json (str): Message in json format.
        delay_multiplier (int): Delay multiplier. Default=10.
        timeout (Optional[int]): Timeout in seconds. Default=120s.

    Returns:
        None
    """
    log.debug(msg=f"Received a request to send {len(list_of_messages)} to queue {queue_name}.")
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_conn_str, logging_enable=True)

    with servicebus_client:
        servicebus_sender = servicebus_client.get_queue_sender(queue_name=queue_name)

        list_of_service_bus_messages = build_list_of_service_bus_messages(
            list_of_messages=list_of_messages,
            delay_multiplier=delay_multiplier,
            timeout=timeout,
            func_get_scheduled_enqueue_time_utc=get_scheduled_enqueue_time_utc,
        )

        with servicebus_sender:
            batch_message = build_batch_message(
                list_of_service_bus_messages=list_of_service_bus_messages, sender=servicebus_sender
            )

            servicebus_sender.send_messages(message=batch_message)

            log.info(msg=f"Sent {len(list_of_service_bus_messages)} messages to queue {queue_name}.")
