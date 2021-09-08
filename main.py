import json
import requests
from requests import Request, Response

from handlers.config_handler import load_config
from handlers.log_handler import create_logger

log = create_logger(__name__)

API = "https://puush.me/api/"
AUTH_API = "{}/auth".format(API)
HISTORY_API = "{}/hist".format(API)
DELETION_API = "{}/del".format(API)
THUMBNAIL_API = "{}/thumb".format(API)
UPLOAD_API = "{}/up".format(API)

config = load_config()


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
    response = requests.post(HISTORY_API, data={"k": config["api_key"]})

    log.debug("Response dict:\n{}".format(response.__dict__))
    log_response(response)
    print_response(response)


if __name__ == '__main__':
    if "api_key" not in config:
        print("Missing config entry: API_KEY, aborting!")
        exit(1)
    if config["api_key"] is None:
        print("Unset config entry: API_KEY, aborting!")
        exit(1)

    # Get history (10 items), in order to get list to start with.
    get_history()

    #
