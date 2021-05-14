# RedAlert
Get toast notification for Red Alerts.

## Simple Explanation
This tool pops a toast notification for every Red Alert.  
You can filter the regions for you notification in the `regions.cfg` file.  
All Red Alert notifications (even filtered ones) are logged to the console and log file.  

## The `regions.cfg` File
Add this file to filter the toast notifications to show specific regions only.  
The file should be place in this directory (you can rename the example file).  
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
So, `ראשון לציון` will notify for both `ראשון לציון - מזרח` and `ראשון לציון - מערב`).  
* This script represents the basic idea.  
Feel free to improve the implementation, add features, GUI, etc.  
Just fork this repository, I'd love to see your work!
