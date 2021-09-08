from __future__ import print_function
import sys
from requests import Response

from handlers.log_handler import create_logger

log = create_logger(__name__)


def log_request(url: str, method="POST"):
    log.info("Sent {method} request to {url}".format(method=method, url=url))


def print_request(url: str, method="POST"):
    print("Sent {method} request to {url}".format(method=method, url=url))


def logprint_request(url: str, method="POST"):
    log_request(url, method)
    print_request(url, method)


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


def logprint_response(response: Response):
    log_response(response)
    print_response(response)


def logprint(*args, **kwargs):
    log.info(*args, **kwargs)
    print(*args, **kwargs)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def logprint_error(*args, **kwargs):
    log.error(*args, **kwargs)
    eprint(*args, **kwargs)