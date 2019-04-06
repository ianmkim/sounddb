from app import *

def get_shows(shows_list):
    namelist = []
    for item in shows_list:
        if item.showName not in namelist:
            namelist.append(item.showName)
    return namelist

