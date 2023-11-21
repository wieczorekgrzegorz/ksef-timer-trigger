"""Sends a message back to the queue with a scheduled delay (default=120s) set up."""
import logging
import os


from azure.servicebus import ServiceBusClient, ServiceBusSender, ServiceBusMessage, ServiceBusMessageBatch

log = logging.getLogger(name="log." + __name__)


def build_list_of_service_bus_messages(list_of_messages: list) -> list[ServiceBusMessage]:
    """Builds a list of ServiceBusMessages."""

    list_of_service_bus_messages = []
    for message in list_of_messages:
        service_bus_message = ServiceBusMessage(body=message)
        list_of_service_bus_messages.append(service_bus_message)

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


def send(list_of_messages: list) -> None:
    """Sends a scheduled message to specified Service Bus Queue.
    Sets up a ServiceBusClient, a ServiceBusSender, a ServiceBusMessage.

    Parameters:
        servicebus_conn_str (str): Service Bus connection string.
        queue_name (str): Queue name.
        message_json (str): Message in json format.
        timeout (Optional[int]): Timeout in seconds. Default=120s.

    Returns:
        None
    """
    queue_name = os.environ["SERVICEBUS_QUEUE_NIP_TO_CHECK"]

    log.debug(msg=f"Received a request to send {len(list_of_messages)} to queue {queue_name}.")
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=os.environ["SERVICEBUS_CONNECTION_STRING"], logging_enable=True
    )

    with servicebus_client:
        servicebus_sender = servicebus_client.get_queue_sender(queue_name=queue_name)

        list_of_service_bus_messages = build_list_of_service_bus_messages(list_of_messages=list_of_messages)

        with servicebus_sender:
            batch_message = build_batch_message(
                list_of_service_bus_messages=list_of_service_bus_messages, sender=servicebus_sender
            )

            servicebus_sender.send_messages(message=batch_message)

            log.info(msg=f"Sent {len(list_of_service_bus_messages)} messages to queue {queue_name}.")
