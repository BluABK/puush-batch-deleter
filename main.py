import time

import requests

from handlers.config_handler import load_config
from handlers.log_handler import create_logger
from puush_entry import PuushEntry
from utils import logprint_request, logprint_response, logprint, logprint_error

log = create_logger(__name__)

API = "https://puush.me/api"
AUTH_API = "{}/auth".format(API)
HISTORY_API = "{}/hist".format(API)
DELETION_API = "{}/del".format(API)
THUMBNAIL_API = "{}/thumb".format(API)
UPLOAD_API = "{}/up".format(API)

API_STATUS_CODES = {
    "0": "Success",
    "-1": "General failure",
    "-2": "Failure: A requested property was not found",
    "-3": "Failure: Hash mismatch"
}

DELETED_ENTRIES_IDS = []

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
    status_code = response_lines.pop(0)

    if status_code != "0":
        error_info = "Got non-zero return code {}".format(status_code)

        # If status code is known, append its meaning.
        if status_code in API_STATUS_CODES:
            error_info += ": {}".format(API_STATUS_CODES[status_code])

        raise Exception("{}, aborting!".format(error_info))

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
        identifier = properties[0]
        date = properties[1]
        url = properties[2]
        filename = properties[3]
        views = properties[4]
        unknown = properties[5]

        if identifier in DELETED_ENTRIES_IDS:
            log.warning("SKIPPING already deleted entry {} from unsanitary API response! "
                        "The API is untrustworthy, this is sadly expected.".format(identifier))

            continue

        entries.append(PuushEntry(identifier, date, url, filename, views, unknown))

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

    # Prematurely ipdate list of deleted entries' IDs, as it is used by response_texts_to_entries.
    DELETED_ENTRIES_IDS.append(puush.identifier)

    # Delete the given puush by id and store the updated list of puush (history?) entries
    return response_texts_to_entries(make_post_request(
        DELETION_API, data={"k": config["api_key"], "i": entry.identifier}))


def add_unique_puush_entries(src: list, dst: list, id_blacklist: list):
    """
    Adds items from source list to destination list,
    if they are not already in destination list.
    :param src:
    :param dst:
    :param id_blacklist:
    :return:
    """
    for src_entry in src:
        if src_entry.identifier in id_blacklist:
            log.warning("Skipped adding blacklisted PuushEntry to history: {}".format(str(src_entry)))
            continue

        if not any(dst_entry.identifier == src_entry.identifier for dst_entry in dst):
            dst.append(src_entry)
            log.debug("Added new PuushEntry to history: {}".format(str(src_entry)))
        else:
            log.debug2("Skipped adding existing PuushEntry to history: {}".format(str(src_entry)))


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
        while True:
            # Get (hopefully) updated list of items from API.
            history_entries = get_history()

            if len(history_entries) == 0:
                break

            # For every puush entry in current history.
            for puush in history_entries:
                try:
                    # Stagger deletions to not spam API.
                    time.sleep(config["api_rate_limit_delay_seconds"])

                    if puush.identifier in DELETED_ENTRIES_IDS:
                        error_msg = "Attempted to delete Puush with ID {ident}, " \
                                    "but it has already been deleted, skipping and removing from history!".format(
                                        ident=puush.identifier)

                        logprint_error(error_msg)

                        # Skip this iteration of the loop, as it contains flaws.
                        continue

                    # Perform deletion, which returns a history list with this item *supposedly* omitted.
                    updated_history = delete_puush_entry(puush)

                    # Add new unique entries to the history.
                    add_unique_puush_entries(history_entries, updated_history, id_blacklist=DELETED_ENTRIES_IDS)

                    # Make *EXTRA* sure that deleted entries don't still linger in the list we're iterating.
                    for entry in history_entries:
                        if entry.identifier in DELETED_ENTRIES_IDS:
                            log.warning("Removing already deleted entry {} from history entries!".format(
                                entry.identifier))
                            history_entries.pop(history_entries.index(entry))

                    log.debug2([str(x) for x in history_entries])

                except Exception as exc:
                    log.exception(exc)
                    print("{}: {}".format(exc.__class__.__name__, str(exc)))
                    raise

    except Exception as exc:
        log.exception(exc)
        print("{}: {}".format(exc.__class__.__name__, str(exc)))
        raise

