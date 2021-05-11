# RedAlert
Simple python program that notifies Red Alerts

## Simple Explanation
This script shows a Windows notification to the user that contains the numbers of regions that just recieved Red Alert.

The regions that will show the user a notification are writen in a configuration file called `regions.cfg`, and it should be located under the same directory as the Python script.

In the console you will see all the alerted regions, even if you configuted it to not notify you (you can think of it as a 'silent' notification).

## The `regions.cfg` File
In order to get alerts of specific regions only, you need to configure the program.
To do that, you simply need to add a file called `regions.cfg` in the same directory as the Python script.
The proper format of the configuration file is a list numbers that represent the regions, like that:
```
אשקלון
אשדוד
ראשון לציון
```
By using these numbers, you will recieve a notification when a Red Alert is heard in one of those regions.
To know the region numbers by a city, use the Pikud-Ha'Oref feature [here](https://www.oref.org.il/11093-he/Pakar.aspx).

## Installation
1. Run `pip install -r requirements.txt` to install all the required libraries.

## How To Run It
You can run the script in the same way you run any Python script.
Just make sure that you use a Python 3.6 or any other Python 3 version.

## Notes
This is a simple script that should represent the basic idea.<br>
Feel free to improve the implementation, add features, add GUI, etc.<br>
Just fork this repository, I would love to see your work!
