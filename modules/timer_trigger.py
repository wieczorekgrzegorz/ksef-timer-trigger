"""Function triggered by timer. Queries Azure Storage Table to get list of clients to check KSeF for."""
import datetime
import json
import logging

import requests

log = logging.getLogger(name="log." + __name__)

QUERY_ELEM_REF_NO: None = None
PART_ELEM_REF_NO: None = None
ITERATION: int = 0
HEADERS: dict = {"Content-Type": "application/json"}


def build_request_body(table_name: str, operation: str, row_key: str) -> str:
    """Builds JSON-serialized request body for query_clients_config.main()."""

    return json.dumps(
        obj={
            "operation": operation,
            "table_name": table_name,
            "entity": {"RowKey": row_key},
        }
    )


def query_clients_config_table(
    storage_acc_access_point: str,
    timeout: int,
    headers: dict,
    request_body: str,
    api_key: str,
) -> dict:
    """Sends a request to the storage_account_connector function to query the ClientConfig table."""

    response = requests.post(
        url=storage_acc_access_point,
        timeout=timeout,
        headers=headers,
        data=request_body,
        params={"code": api_key},
    )
    log.debug(msg=f"Received response: {response.content}")
    try:
        response_json = response.json()
    except json.decoder.JSONDecodeError as e:
        log.error(msg=f"JSONDecodeError Error while decoding azure storage table response: {response.content}")
        raise e

    return response_json


def checked_recently(datetime_string: str, target_timedelta: datetime.timedelta) -> bool:
    """Checks if the client was checked for KSeF data within last >>target<<
    The purpose of that is to avoid rechecking accounts that have been successfully checked in last run,\
        in order to focus on those that resulted in errors only."""
    try:
        utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        last_successful_run = datetime.datetime.fromisoformat(datetime_string)
        return (utc_now - last_successful_run) < target_timedelta
    except ValueError:
        # if datetime_string is not in isoformat, it means it's a default value from the table, "null" or "None"
        return False
    except TypeError as err:
        log.error(msg=f"TypeError: {err}")
        raise err


def create_list_of_messages(query_result: list[dict], re_run_interval: datetime.timedelta) -> list[str]:
    """Builds list of messages to be sent to the sbq-nips-to-check queue,
    filtering out those that were checked recently."""
    list_of_messages = []
    for item in query_result:
        if (
            checked_recently(datetime_string=item["last_successfull_download_run"], target_timedelta=re_run_interval)
            is False
        ):
            message = {
                "NIP": item["PartitionKey"],
                "last_successful_downloads": [
                    item["last_successfull_download_run"],
                    item["penultimate_successfull_download_run"],
                ],
                "iteration": ITERATION,
                "query_elem_ref_no": QUERY_ELEM_REF_NO,
                "part_elem_ref_no": PART_ELEM_REF_NO,
            }

            try:
                body = json.dumps(obj=message)
            except TypeError as e:
                log.error(msg=f"TypeError while serializing message: {message}")
                raise e

            list_of_messages.append(body)

    return list_of_messages


def main(  # pylint: disable=R0913:too-many-arguments
    storage_acc_access_point: str,
    api_key: str,  # //TODO remove api_key when moved to Azure AD
    table_name: str = "ClientConfig",
    operation: str = "get_all",
    row_key: str = "_zakup",
    timeout: int = 90,
    re_run_interval: datetime.timedelta = datetime.timedelta(hours=2),
) -> list[str]:
    """
    Queries Azure Storage Table to get list of clients to check KSeF for.

    Parameters:
        storage_acc_access_point (str): access point to the storage_account_connector function
        api_key (str): api key for connecting with azure functions #TODO move to AD
        table_name (str, optional): name of the table to query. Default: ClientConfig
        operation (str, optional): operation to perform on the table. Default: get_all
        row_key (str, optional): row key of the entity to query. Default: _zakup
        timeout (int, optional): timeout for connecting with storage_account_connector function. Default: 90s
        re_run_interval (datetime.timedelta, optional): interval after which to recheck the client for KSeF data.\

    Returns:
        list[str]: list of messages to be sent to the sbq-nips-to-check queue.

    Raises:
        ValueError: if error occurs while querying the ClientConfig table
        json.decoder.JSONDecodeError: if error occurs while decoding the response\
            from the storage_account_connector function

    Example of a message list:
        [
            '{"NIP": "1111111111", "last_successful_downloads": ["1900-01-01T00:00:00+00:00",
                "1900-01-01T00:00:00+00:00"], "iteration": 0, "query_elem_ref_no": null, "part_elem_ref_no": null}',
            '{"NIP": "5272097306", "last_successful_downloads": ["1970-01-01T00:00:00+00:00",
                "1970-01-01T00:00:00+00:00"], "iteration": 0, "query_elem_ref_no": null, "part_elem_ref_no": null}',
            '{"NIP": "9999999999", "last_successful_downloads": ["1900-01-01T00:00:00+00:00",
                "1900-01-01T00:00:00+00:00"], "iteration": 0, "query_elem_ref_no": null, "part_elem_ref_no": null}',
        ]
    """

    request_body = build_request_body(table_name=table_name, operation=operation, row_key=row_key)

    log.debug(msg="Querying ClientsConfig for list of NIPs to check.")
    response_json = query_clients_config_table(
        storage_acc_access_point=storage_acc_access_point,
        timeout=timeout,
        headers=HEADERS,
        request_body=request_body,
        api_key=api_key,
    )
    log.debug(msg=f"Received response: {response_json}")

    if response_json["error"] is not None:
        log.error(msg=f"Error while querying ClientsConfig: {response_json['error']}")
        raise ValueError(f"Error: {response_json['error']}.")

    return create_list_of_messages(query_result=response_json["query_result"], re_run_interval=re_run_interval)
