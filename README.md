# RedAlert
Get toast notifications for Red Alerts.

You can filter the notifications by listing your regions in the `regions.cfg` file.  
All Red Alert notifications (even filtered ones) are logged to the console and log file.  

## The `regions.cfg` File
Add this file to the repository's directory to filter the toast notifications.  
The file should contain a list of regions (splitted by new-lines).  
For example:
```
תל אביב
אשדוד
ראשון לציון
```
This way you'll receive toast notifications for those regions only.  
To find your region, refer to [Pikud-Ha'Oref](https://www.oref.org.il/).

## Installation & Usage
```sh
pip install -r requirements.txt
python red_alert.py
```

## Notes
* The regions in `regions.cfg` are searched in the text, not compared to it.  
So, `ראשון לציון` will notify for both `ראשון לציון - מזרח` and `ראשון לציון - מערב`.  
* Feel free to improve my implementation, add features, GUI, etc.  
You can send a PR when you're finished. I'd love to see your work!
