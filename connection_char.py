#########################################################
# Script used to define functions used to manage the    #
# pool placement, characterization, client pinging and  #
# timestamp assignment and checking                     #
#########################################################

import time
import ConfigParser
from threading import Lock

parser = ConfigParser.ConfigParser()
parser.read('config.ini')
check_time = int(parser.get("Settings", "check_time"))
threshold = int(parser.get("Settings", "timestamp_threshold"))
current_time = int(time.time())
lock_place = Lock()
lock_remove = Lock()

#MISSING: port specification

def placeinPool(client,timestamp):
    lock_place.acquire()
    try:
        print("PLACING IN POOL CLIENT: {}".format(client))
        POOL[client] = [timestamp, "characterization"]
    finally:
        lock_place.release()

def removefromPool(client):
    lock_remove.acquire()
    try:
        print("REMOVING FROM POOL CLIENT: {}".format(client))
        POOL.pop(client)
    finally:
        lock_remove.release()
    
def characterize(client):
    #TO COMPLETE
    print("CHARACTERIZING")

def assignTimestamp(client):
    print("ASSIGNING TIMESTAMP")
    tstamp = int(time.time())
    TIMESTAMPS[client] = tstamp
    return tstamp

def classifyConnection(client):
    #Check if timestamp present and if valid
    print("CHECKING FOR TIMESTAMP")
    if(client in TIMESTAMPS.keys() and True):
        print("TIMESTAMP FOUND! PLACING IN POOL")
        placeinPool(client,TIMESTAMPS[client])
    else:
        print("TIMESTAMP NOT FOUND, PROCEEDING")
        characterize(client)
        timestamp = assignTimestamp(client)
        placeinPool(client,timestamp)    

def checkTimestamp():
    if(len(POOL) > 0):
        for client in POOL.keys():
            ip = client.split(":")[0]
            port = client.split(":")[1]
            print("Checking client: " + client)
            current_time = int(time.time())
            time_dif = current_time - POOL[client][0]
            if(time_dif > threshold):
                print("bad timestamp")
                removefromPool(client)
                characterize(client)
                timestamp = assignTimestamp(client)
                placeinPool(client,timestamp)
            else:
                print("good timestamp, nothing to do here")
                #pass
    else:
        pass

POOL = {}
TIMESTAMPS = {}
