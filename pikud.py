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
CURRENT_ALERTS = set()
ALERT_TIME = 30
NOTIFIER = ToastNotifier()



def load_regions():
    """
    Loads the regions that interest the user from the regions.cfg file.
    """
    # Make sure that the config file exists before trying to access it
    if os.path.exists(REGIONS_FILE_PATH):
        # Load the regions from the config file
        USER_REGIONS = open(REGIONS_FILE_PATH ,"r").readlines()
        
        # Remove '\n' from the end of every line, and remove empty lines
        USER_REGIONS = list(map(lambda line: line.strip(), USER_REGIONS))
        USER_REGIONS = set(filter(lambda line: line != '', USER_REGIONS))
        
        print(f"Found {len(USER_REGIONS)} regions in the config file.")
        if len(USER_REGIONS) > 0:
            print("You'll receive a notification when Red Alert hits these regions:")
            print(', '.join(USER_REGIONS))
    else:
        print('No /regions.cfg file found.')
    print('-' * 32)
    return USER_REGIONS


def get_current_alerts():
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


def notify_user(region):
    """
    Shows an Windows alert to the user that contains the region name.
    """
    NOTIFIER.show_toast("Red Alert!", msg=region)
    

def handle_region(region):
    """
    Saves the region in the alerts list, and removes it when the time comes. 
    """
    if region in USER_REGIONS and region not in CURRENT_ALERTS:
        CURRENT_ALERTS.add(region)
        timer = threading.Timer(ALERT_TIME, lambda: CURRENT_ALERTS.remove(region))
        timer.start()
        notify_user(region)
        print("Notified")


def print_silent_alerts(regions):
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
            # Handle every region in the current alerts
            for region in current_alerts_data["data"]:
                handle_region(region)
            # Print all the current regions to the console as "silent" alerts
            print_silent_alerts(current_alerts_data["data"])
            
        # Make the request to Pikud Ha'Oref's link every 1 second
        time.sleep(1)

if __name__ == "__main__":
    main()    