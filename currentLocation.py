from geopy.geocoders import Nominatim
from random import randrange

geoLoc = Nominatim(user_agent="GetLoc")

def getLocation():
    latitude = 45.419510 
    longitude = -75.678770
    for i in range(10):
        result = str(latitude)+", "+str(longitude)
        locname = geoLoc.reverse(result)
        print(locname.address)
        latitude+=1
        longitude+=1
        i=i-1
    

def displayLocation():
    latitude = 45.419510 
    longitude = -75.678770
    displayResult = str(latitude)+", "+str(longitude)  
    displayLocname = geoLoc.reverse(displayResult)
    return displayLocname