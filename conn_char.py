#########################################################
# Script used to define functions used to manage the    #
# pool placement, characterization, client pinging and  #
# timestamp assignment and checking                     #
#########################################################

import time
import ConfigParser

parser =  ConfigParser.ConfigParser()
parser.read('config.ini')
check_time = int(parser.get("Settings", "check_time"))
threshold = int(parser.get("Settings", "timestamp_threshold"))
current_time = int(time.time())

#MISSING: port specification

def placeinPool(client,timestamp):
    print("PLACING IN POOL")
    POOL[client] = [timestamp, "characterization"]

def removefromPool(client):
    print("REMOVING FROM POOL")
    POOL.pop(client)

def characterize(client):
    print("CHARACTERIZING")

def assignTimestamp(client):
    print("ASSIGNING TIMESTAMP")
    #tstamp = time.ctime(time.time())
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

def pingClient(client):
    return True

def checkTimestamp():
    if(len(POOL) > 0):
        for client in POOL.keys():
            ip = client.split(":")[0]
            port = client.split(":")[1]
            #Check if client anwers to ping
            print("revision")
            if(pingClient(client)):
                #Check if timestamp is below threshold
                print("ping succesfull")
                current_time = int(time.time())
                time_dif = current_time - POOL[client][0]
                if(time_dif > threshold):
                    print("bad timestamp")
                    characterize(client)
                    timestamp = assignTimestamp(client)
                    placeinPool(client,timestamp)
                else:
                    print("good itmestamp, nothing to see here")
                    #pass
            else:
                removefromPool(client)

POOL = {}
TIMESTAMPS = {}
