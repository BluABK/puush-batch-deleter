import time

import requests

from handlers.config_handler import load_config
from handlers.log_handler import create_logger
from puush_entry import PuushEntry
from utils import logprint_request, logprint_response, logprint

log = create_logger(__name__)

API = "https://puush.me/api"
AUTH_API = "{}/auth".format(API)
HISTORY_API = "{}/hist".format(API)
DELETION_API = "{}/del".format(API)
THUMBNAIL_API = "{}/thumb".format(API)
UPLOAD_API = "{}/up".format(API)

config = load_config()


def make_post_request(api_endpoint: str, data: dict):
    """
    Makes a HTTP POST request to an API endpoint, with an optional data payload.
    :param api_endpoint:
    :param data:
    :return:
    """
    response = requests.post(api_endpoint, data=data)
    logprint_request(api_endpoint)

    logprint_response(response)
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

    return response_lines


def response_texts_to_entries(texts: list):
    """
    Takes a list of strings and creates a list of PuushEntry objects from it.
    :param texts:
    :return:
    """
    entries = []

    # Remove empty text entries.
    for i in range(len(texts)):
        if texts[i] == "":
            texts.pop(i)

    for text in texts:
        # Split string into a list.
        properties = text.split(',')

        entries.append(PuushEntry(*properties))

    return entries


def get_history():
    """
    Puush History API request which returns up to 10 entries, if successful.
    :return:
    """
    return response_texts_to_entries(make_post_request(HISTORY_API, data={"k": config["api_key"]}))


def delete_puush_entry(entry: PuushEntry):
    """
    Puush Deletion API request which deletes a given PuushEntry and
    returns an updated list of puush (history?) entries.
    :param entry:
    :return:
    """
    if entry.identifier is None:
        raise Exception("PuushEntry identifier was None!")

    logprint("Deleting Puush entry \"{name}\" (ID: {ident})...".format(name=entry.filename,
                                                                       ident=entry.identifier))

    # Delete the given puush by id and store the updated list of puush (history?) entries
    return response_texts_to_entries(make_post_request(
        DELETION_API, data={"k": config["api_key"], "i": entry.identifier}))


def add_unique_puush_entries(src: list, dst: list):
    """
    Adds items from source list to destination list,
    if they are not already in destination list.
    :param src:
    :param dst:
    :return:
    """
    for src_entry in src:
        if not any(dst_entry.identifier == src_entry.identifier for dst_entry in dst):
            dst.append(src_entry)


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

        # While history holds item, systematically delete them.
        for puush in history_entries:
            try:
                # Stagger deletions to not spam API.
                time.sleep(0.5)

                # Perform deletion and add new unique entries to the history.
                add_unique_puush_entries(history_entries, delete_puush_entry(puush))
                log.debug2(history_entries)

                for entry in history_entries:
                    log.debug(entry)
            except Exception as exc:
                log.exception(exc)
                print("{}: {}".format(exc.__class__.__name__, str(exc)))
                raise

    except Exception as exc:
        log.exception(exc)
        print("{}: {}".format(exc.__class__.__name__, str(exc)))
        raise

