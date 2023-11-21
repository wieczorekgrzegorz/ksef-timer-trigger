# Timer Trigger API

The `timer_trigger_api` is an Azure Function that is triggered by a timer. It runs every hour, on the first second of the first minute. The function is responsible for retrieving a list of clients to check KSeF for and sending a message to the internal Service Bus Queue for each client.

## Functionality

The function uses the list_of_clients.get function to query an Azure Storage Table for a list of clients. The storage account access point and API key are retrieved from the configuration.

Once the list of clients is retrieved, the function uses the messages_to_queue.send function to send a message to the internal Service Bus Queue for each client. The Service Bus connection string and queue name are also retrieved from the configuration.

## Usage

The function is automatically triggered every hour, so there's no need to manually trigger it. However, it can be manually triggered for testing purposes.

## Configuration

The function requires the following configuration values:

- `STORAGE_TABLE_CONNECTOR_ACCESS_POINT`: The access point to the Azure Storage Table.
- `STORAGE_TABLE_CONNECTOR_API_KEY`: The API key for connecting with the Azure Storage Table.
- `SERVICEBUS_CONNECTION_STRING`: The connection string for the Azure Service Bus.
- `QUEUE_INTERNAL`: The name of the internal Service Bus Queue.

These configuration values should be set in the 'config' module.

## Testing

To run the tests, navigate to the project root directory and run the following command:

```bash
python -m unittest discover tests
```

This will automatically discover and run all the tests in the tests/ directory. Make sure to install all the necessary dependencies before running the tests. You can do this by running:

```bash
pip install -r requirements.txt
```
