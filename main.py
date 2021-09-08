import json
import requests
from requests import Request, Response

from handlers.config_handler import load_config
from handlers.log_handler import create_logger
from puush_entry import PuushEntry

log = create_logger(__name__)

API = "https://puush.me/api"
AUTH_API = "{}/auth".format(API)
HISTORY_API = "{}/hist".format(API)
DELETION_API = "{}/del".format(API)
THUMBNAIL_API = "{}/thumb".format(API)
UPLOAD_API = "{}/up".format(API)

config = load_config()


def log_request(url: str, method="POST"):
    log.info("Sent {method} request to {url}".format(method=method, url=url))


def print_request(url: str, method="POST"):
    print("Sent {method} request to {url}".format(method=method, url=url))


def log_response(response: Response):
    log.info("Received {method} request response {code} ({reason}){server} "
             "in {elapsed}".format(
                method=response.request.method.upper(),
                server=" from server '{}'".format(
                    response.headers.get("Server")) if "Server" in response.headers.keys() else "",
                elapsed=str(response.elapsed),
                reason=response.reason,
                code=response.status_code))


def print_response(response: Response):
    print("Received {method} request response {code} ({reason}){server} "
          "in {elapsed}".format(
                method=response.request.method.upper(),
                server=" from server '{}'".format(
                    response.headers.get("Server")) if "Server" in response.headers.keys() else "",
                elapsed=str(response.elapsed),
                reason=response.reason,
                code=response.status_code))


def get_history():
    entries = []
    response = requests.post(HISTORY_API, data={"k": config["api_key"]})
    log_request(HISTORY_API)
    print_request(HISTORY_API)

    log_response(response)
    print_response(response)
    log.debug("Response dict:\n{}".format(response.__dict__))

    # Split response text into list of strings.
    response_lines = response.text.split('\n')
    log.info(response_lines)

    # Pop the first entry from the lines as it is a status code, and save it in its own variable.
    status_code = int(response_lines.pop(0))

    if status_code != 0:
        raise Exception("Got non-zero return code: {}, aborting!".format(status_code))

    # Remove empty entries
    for i in range(len(response_lines)):
        if response_lines[i] == "":
            response_lines.pop(i)

    for line in response_lines:
        # Split string into a list.
        properties = line.split(',')

        entries.append(PuushEntry(*properties))

    return entries


if __name__ == '__main__':
    if "api_key" not in config:
        print("Missing config entry: API_KEY, aborting!")
        exit(1)
    if config["api_key"] is None:
        print("Unset config entry: API_KEY, aborting!")
        exit(1)

    # Get history (10 items), in order to get list to start with.
    try:
        history_entries = get_history()

        log.info([str(x) for x in history_entries])
        for entry in history_entries:
            print(entry)
    except Exception as exc:
        log.exception(exc)
        print("{}: {}".format(exc.__class__.__name__, str(exc)))

