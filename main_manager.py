#########################################################
# Main script that will call all the needed functions   #
# for the server to work as well as read specifications #
# from a config file.                                   #
#########################################################

import ConfigParser
import signal
import sys
from twisted.internet import task, reactor
from server_init import *

#Function used to handle the closing of the server after 
#CTRL + C is pressed
def signal_handler(sig, frame):
    print("Exiting server")
    server.stop()
    server.join()
    sys.exit(0)

if __name__=="__main__":
    parser =  ConfigParser.ConfigParser()
    parser.read('config.ini')
    HOST = parser.get('Settings', 'host_manager')
    PORT = int(parser.get('Settings', 'port_manager'))
    MAX_CLIENTS = int(parser.get('Settings', 'max_clients'))
    CHECK_TIME = int(parser.get('Settings', 'check_time'))
    server = SocketServer(HOST,PORT,MAX_CLIENTS)
    server.daemon = True
    server.start()
    #Neded to check every x time for the timestamps of the clients in the pool
    checker = task.LoopingCall(checkTimestamp)
    checker.start(CHECK_TIME)
    reactor.run()

    signal.signal(signal.SIGINT, signal_handler)
    while True:
        q = raw_input("Check for pool: ")
        if(q == 'Y'):
           print(server.sock_pool)
           print(server.sock_timestamp)
       #pass

