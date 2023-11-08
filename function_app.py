"""Azure Function triggered by timer trigger.
Connects with Storage Table API to get list of clients to check KSeF for and sends message
to the internal Service Bus Queue for each client."""
import logging
import azure.functions as func

from modules import timer_trigger, send_msg_to_queue
from modules.utilities import config, logger

log = logging.getLogger(name="log." + __name__)
logger.set_up(level=logging.DEBUG)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.function_name(name="TimerTrigger")
@app.service_bus_queue_output(
    arg_name="queuemsg",
    connection=config.SERVICEBUS_APP_SETTING_NAME,
    queue_name=config.QUEUE_INTERNAL,
)
@app.schedule(
    schedule="0 0 * * * *",
    arg_name="timer",
    run_on_startup=True,
    use_monitor=False,
)
# pylint: disable=unused-argument
def timer_trigger_api(timer: func.TimerRequest) -> None:
    """
    TimerTrigger function that runs every hour. Sends a message to the internal queue,
    to trigger the ClientTableChecker function.
    """
    log.info(msg="Timer trigger started.")
    list_of_messages = timer_trigger.main(
        storage_acc_access_point=config.STORAGE_TABLE_CONNECTOR_ACCESS_POINT,
        api_key=config.STORAGE_TABLE_CONNECTOR_API_KEY,
    )

    if len(list_of_messages) == 0:
        log.info(msg="No messages to send.")
    else:
        log.info(msg=f"Sending {len(list_of_messages)} messages to queue.")

    for message in list_of_messages:
        # //TODO: modify send_msg_to_queue to use the ServiceBusClient and ServiceBusSender objects
        # https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-queues?tabs=connection-string
        send_msg_to_queue.main(
            servicebus_conn_str=config.SERVICEBUS_CONNECTION_STRING,
            queue_name=config.QUEUE_INTERNAL,
            message_json=message,
        )
