import requests
import time
import datetime
import json
import threading
import os
import logging

REGIONS_FILE_PATH = "regions.cfg"
PIKUD_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
PIKUD_REFERER = "https://www.oref.org.il/"
USER_REGIONS = set()
CURRENT_ALERTS = set()
ALERT_TIME = 30
REFRESH_TIME = 0.5

# Set a logger & log formatter
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
log_formatter = logging.Formatter(
    '%(asctime)s  %(levelname)s: %(message)s')
console_log_formatter = logging.Formatter('%(asctime)s %(message)s')

# Setup logging to a log file
log_handler = logging.FileHandler(filename='log.txt', mode='a', encoding='utf-8')
log_handler.setFormatter(log_formatter)
print_handler = logging.StreamHandler()
print_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.addHandler(print_handler)

try:
    from win10toast import ToastNotifier
except:
    logger.debug("Could not import win10toast (no toasts available)")
    from unittest.mock import Mock as ToastNotifier

NOTIFIER = ToastNotifier()


def load_regions() -> set:
    """ 
    Loads the regions from regions.cfg file.
    """
    global USER_REGIONS

    try:
        # Load the regions from the config file
        with open(REGIONS_FILE_PATH, "r", encoding='utf-8') as f:
            USER_REGIONS = f.readlines()

        # Remove '\n' from the end of every line, and remove empty lines
        USER_REGIONS = list(map(lambda line: line.strip(), USER_REGIONS))
        USER_REGIONS = set(filter(lambda line: line != '', USER_REGIONS))

        logger.info(f"Found {len(USER_REGIONS)} regions in the config file.")
        if len(USER_REGIONS) > 0:
            logger.info("You'll receive a notification when Red Alert hits these regions:")
            logger.info(', '.join(USER_REGIONS))
        else:
            USER_REGIONS = None
            logger.warning('No regions specified in the configuration file.')
            logger.warning(
                'Visit the GitHub page to see how to do that: https://github.com/idan22moral/RedAlert')
    except FileNotFoundError:
        # Set USER_REGIONS = None to indicate that the user has no preferences
        # In this case the user will a toast notification for any region
        USER_REGIONS = None
        logger.warning(f'No ./{REGIONS_FILE_PATH} file found.')

    return USER_REGIONS

def get_current_alerts() -> str:
    """
    Returns a json (dict) that contains the data from the alert source.
    """
    headers = {
        'Referer':          PIKUD_REFERER,
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.get(PIKUD_URL, headers=headers)
    json_data = response.json()
    return json_data

def notify_user(regions: str) -> None:
    NOTIFIER.show_toast(title="Red Alert!", msg=regions, threaded=True)

def end_alert(region: str) -> None:
    try:
        CURRENT_ALERTS.remove(region)
    except KeyError as e:
        pass

def filter_new_regions(regions: list) -> list:
    """
    Returns only the new regions from the given regions list.
    """
    global CURRENT_ALERTS
    # Remove already alerted regions from the list
    new_regions = [region for region in regions if region not in CURRENT_ALERTS]
    return new_regions

def filter_user_regions(regions: list):
    """
    Returns only the regions that match the user's regions.
    """
    global USER_REGIONS
    if USER_REGIONS == None:
        return regions
    else:
        # Remove the irrelevant regions from the list, if the user has any prefrences
        return [region for region in regions if any([x in region for x in USER_REGIONS])]

def alert_regions(regions: list) -> list:
    """
    Sets a timer of ALERT_TIME seconds, and notifies the user about all the `regions`.
    When ALERT_TIME seconds pass, new alerts about `regions` can be alerted.
    The timer is set to prevent alert-flooding about the same regions.
    """
    # Add the regions to the list of already alerted regions
    # and set a timer for every region
    for region in regions:
        CURRENT_ALERTS.add(region)
        timer = threading.Timer(ALERT_TIME, end_alert, args=(region,))
        timer.daemon = True
        timer.start()
        logger.info(f"USER ALERTS: {region}")

    # Notify the user about all the new regions
    if len(regions) > 0:
        notify_user(', '.join(regions))

def log_silent_alerts(regions: list) -> None:
    for region in regions:
        logger.info(f"SILENT ALERT: {region}")

def main():
    # Load the regions from the config file
    global USER_REGIONS, REFRESH_TIME
    USER_REGIONS = load_regions()
    while True:
        try:
            current_alerts = get_current_alerts()
            
            new_regions = filter_new_regions(current_alerts["data"])
            log_silent_alerts(new_regions)

            user_regions = filter_user_regions(new_regions)
            alert_regions(user_regions)
        except json.JSONDecodeError:
            pass
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            logger.error(str(e))
            
        # Make the request to Pikud-Ha'Oref's link every 1 second
        try:
            time.sleep(REFRESH_TIME)
        except KeyboardInterrupt:
            exit()


if __name__ == "__main__":
    main()
