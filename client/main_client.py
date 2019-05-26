#########################################################
# Main script that will call all the needed functions   #
# for the client to work as either a client or a server #
# respectively.                                         #
#########################################################

#import socket
import threading
import ConfigParser
from client_init import *

if __name__=="__main__":
    parser =  ConfigParser.ConfigParser()
    parser.read('config.ini')
    HOST_MANAGER = parser.get('Settings', 'host_manager')
    PORT_MANAGER = int(parser.get('Settings', 'port_manager'))
    client = SocketClient(HOST_MANAGER,PORT_MANAGER)
    client.daemon = True
    client.start()

ct = 0
while True:
    if(ct == 0):
        message = raw_input()
    else:
        message = raw_input("Enter command: \n")
    ct += 1 

    if message == 'Disconnect':
        break
    elif message == 'Pair':
        thread = threading.Thread(target=pairClient)
        thread.daemon = True
        try:
            client.close()
            thread.start()
        except:
            thread.close()
            break

