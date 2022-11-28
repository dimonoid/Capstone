from gps import *
import time
from geopy.geocoders import Nominatim

running = True

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

def getPositionData(gps):
    nx = gpsd.next()
    geoLoc = Nominatim(user_agent="GetLoc")

    if nx['class'] == 'TPV':
        latitude = getattr(nx,'lat', "Unknown")
        longitude = getattr(nx,'lon', "Unknown")
        result = str(latitude)+", "+str(longitude)
        locname = geoLoc.reverse(result)
        displayLocation = "Your position: lon = " + str(longitude) + ", lat = " + str(latitude)
        print("Your position: lon = " + str(longitude) + ", lat = " + str(latitude))
        print(locname.address)
        return displayLocation

try:
    print("Application started!")
    while running:
        getPositionData(gpsd)
        time.sleep(1.0)

except (KeyboardInterrupt):
    running = False
    print("Applications closed!")