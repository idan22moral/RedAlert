import requests
import time
import datetime
try:
    from win10toast import ToastNotifier
except:
    from unittest.mock import Mock as ToastNotifier
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
NOTIFIER = ToastNotifier()

# Set a logger & log formatter
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
file_log_formatter = logging.Formatter(
    '%(asctime)s  %(levelname)s: %(message)s')
console_log_formatter = logging.Formatter('%(asctime)s %(message)s')

# Setup logging to a log file
file_log_handler = logging.FileHandler(filename='log.txt', mode='a', encoding='utf-8')
file_log_handler.setFormatter(file_log_formatter)
logger.addHandler(file_log_handler)


def load_regions() -> set:
    """
    Loads the regions that interest the user from the `regions.cfg` file.
    """
    global USER_REGIONS

    try:
        # Load the regions from the config file
        with open(REGIONS_FILE_PATH, "r") as f:
            USER_REGIONS = f.readlines()

        # Remove '\n' from the end of every line, and remove empty lines
        USER_REGIONS = list(map(lambda line: line.strip(), USER_REGIONS))
        USER_REGIONS = set(filter(lambda line: line != '', USER_REGIONS))

        print(f"Found {len(USER_REGIONS)} regions in the config file.")
        if len(USER_REGIONS) > 0:
            print("You'll receive a notification when Red Alert hits these regions:")
            print(', '.join(USER_REGIONS))
        else:
            USER_REGIONS = None
            print('No regions specified in the configuration file.')
            print(
                'Visit the GitHub page to see how to do that: https://github.com/idan22moral/RedAlert')
    except FileNotFoundError:
        # Set USER_REGIONS as None to indicate the fact that the user has no prefrences
        # In this case the user shoud recieve an alert for every possible region
        USER_REGIONS = None
        print('No /regions.cfg file found.')

    print('-' * 32)
    return USER_REGIONS


def get_current_alerts() -> str:
    """
    Returns a string that contains the json data from the alert source.
    Note: when there are no alerts, the string is empty.
    """
    headers = {
        'Referer':          PIKUD_REFERER,
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.get(PIKUD_URL, headers=headers)
    return response.text


def notify_user(regions: str) -> None:
    """
    Shows a Windows alert to the user that contains the region name.
    """
    NOTIFIER.show_toast("Red Alert!", regions)


def end_alert(region: str) -> None:
    """
    Removes `region` from the CURRENT_ALERTS list.
    This function as the callback of every timer, 
    to be ableto receive of new alerts about `region`.
    """
    try:
        CURRENT_ALERTS.remove(region)
    except KeyError as e:
        pass


def alert_regions(regions: list) -> None:
    """
    Sets a timer of ALERT_TIME seconds, and notifies the user about all the `regions`.
    When ALERT_TIME seconds pass, new alerts about `regions` can be alerted.
    We use a timer to prevent alert-flooding about the same regions.
    """
    # Remove already alerted regions from the list
    regions_to_alert = [
        region for region in regions if region not in CURRENT_ALERTS]

    # Remove the irrelevant regions from the list, if the user has any prefrences
    if USER_REGIONS != None:
        regions_to_alert = [
            region for region in regions if region in USER_REGIONS]

    # Add the regions to the list of already alerted regions
    # and Set a timer for every region
    for region in regions_to_alert:
        CURRENT_ALERTS.add(region)
        timer = threading.Timer(ALERT_TIME, end_alert, args=(region))
        timer.start()
    # Notify the user about all the new regions
    if len(regions_to_alert) > 0:
        logger.info("USER ALERTS: " + ', '.join(regions_to_alert))
        notify_user(', '.join(regions_to_alert))


def print_silent_alerts(regions: list) -> None:
    """
    Prints all the regions to the console with a timestamp.
    """
    # Make sure that the list is not empty
    if(len(regions) > 0):
        # Get all the numbers of the regions and join them to one string
        region_numbers = ', '.join([region.split(' ')[-1]
                                    for region in regions])
        # Format the current time to a timestamp
        current_time = datetime.datetime.now()
        current_time_formatted = datetime.datetime.strftime(
            current_time, "[%d/%m/%y %H:%M:%S]")
        print(f"{current_time_formatted}: {region_numbers}")
        logger.info("ALERTED REGIONS " + region_numbers)


def main():
    # Load the regions from the config file
    global USER_REGIONS
    USER_REGIONS = load_regions()

    while True:
        current_alerts_raw = ""
        try:
            current_alerts_raw = get_current_alerts()
        except Exception as e:
            print(f'Error: {str(e)}')

        # Check if there are any alerts right now
        if current_alerts_raw != '':
            try:
                # Convert the raw json data from string to dictionary
                current_alerts_data = json.loads(current_alerts_raw)

                # Print all the current regions to the console as "silent" alerts
                print_silent_alerts(current_alerts_data["data"])
                # Handle every region in the current alerts
                alert_regions(current_alerts_data["data"])
            except Exception as e:
                print(f'Error: {str(e)}')

        # Make the request to Pikud-Ha'Oref's link every 1 second
        time.sleep(1)


if __name__ == "__main__":
    main()
