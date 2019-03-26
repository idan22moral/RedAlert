import requests
import time
import datetime
from win10toast import ToastNotifier
import json
import threading
import os

REGIONS_FILE_PATH = "regions.cfg"
PIKUD_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
PIKUD_REFERER = "https://www.oref.org.il/894-he/pakar.aspx"
USER_REGIONS = set()
CURRENT_ALERTS = set()
ALERT_TIME = 30
NOTIFIER = ToastNotifier()



def load_regions() -> set():
    """
    Loads the regions that interest the user from the regions.cfg file.
    """
    global USER_REGIONS

    try:
        # Load the regions from the config file
        with open(REGIONS_FILE_PATH ,"r") as f:
            USER_REGIONS = f.readlines()
    
        # Remove '\n' from the end of every line, and remove empty lines
        USER_REGIONS = list(map(lambda line: line.strip(), USER_REGIONS))
        USER_REGIONS = set(filter(lambda line: line != '', USER_REGIONS))

        print(f"Found {len(USER_REGIONS)} regions in the config file.")
        if len(USER_REGIONS) > 0:
            print("You'll receive a notification when Red Alert hits these regions:")
            print(', '.join(USER_REGIONS))
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


def notify_user(region: str) -> None:
    """
    Shows a Windows alert to the user that contains the region name.
    """
    NOTIFIER.show_toast("Red Alert!", region)


def handle_region(region: str) -> None:
    """
    Sets a timer of ALERT_TIME seconds, and notifies the user about the region.
    When ALERT_TIME seconds pass, new alerts from the given region can be alerted.
    We use a timer to prevent alert flooding about the same region.
    """
    # Check if region is in the user's regions set
    # and make sure that the region is not already alerted
    
    if region in USER_REGIONS and region not in CURRENT_ALERTS:
        # Add the region to the list of current alerts
        CURRENT_ALERTS.add(region)
        # Set a timer for ALERT_TIME
        # When it ends the region will be removed from the alerts list
        timer = threading.Timer(ALERT_TIME, lambda: CURRENT_ALERTS.remove(region))
        timer.start()
        # Notify the user about the red alert in the given region
        notify_user(region)


def alert_regions(regions: list) -> None:
    # Remove already alerted regions from the list
    regions_to_alert = [region for region in regions if region not in CURRENT_ALERTS] 
    
    # Remove the irrelevant regions from the list, if the user has any prefrences
    if USER_REGIONS != None:
        regions_to_alert = [region for region in regions if region in USER_REGIONS]
    
    for region in regions_to_alert:
        CURRENT_ALERTS.add(region)
        timer = threading.Timer(ALERT_TIME, lambda: CURRENT_ALERTS.remove(region))
        timer.start()
    print("Notified")
    notify_user(', '.join(regions_to_alert))
    

def print_silent_alerts(regions: list) -> None:
    """
    Prints all the regions to the console with a timestamp.
    """
    # Make sure that the list is not empty
    if(len(regions) > 0):
        # Get all the numbers of the regions and join them to one string
        region_numbers = ', '.join([region.split(' ')[-1] for region in regions])
        # Format the current time to a timestamp
        current_time = datetime.datetime.now()
        current_time_formatted = datetime.datetime.strftime(current_time, "[%d/%m/%y %H:%M:%S]")
        print(f"{current_time_formatted}: {region_numbers}")


def main():
    # Load the regions from the config file
    global USER_REGIONS
    USER_REGIONS = load_regions()
    
    while True:
        current_alerts_raw = get_current_alerts()
        
        # Check if there are any alerts right now
        if current_alerts_raw is not '':
            # Convert the raw json data from string to dictionary
            current_alerts_data = json.loads(current_alerts_raw)
            
            try:
                # Handle every region in the current alerts
                #for region in current_alerts_data["data"]:
                #    handle_region(region)
                alert_regions(current_alerts_data["data"])
                # Print all the current regions to the console as "silent" alerts
                print_silent_alerts(current_alerts_data["data"])
            except Exception as e:
                print(f'Error: {str(e)}')
            
        # Make the request to Pikud-Ha'Oref's link every 1 second
        time.sleep(1)

if __name__ == "__main__":
    main()    