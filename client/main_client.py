#########################################################
# Main script that will call all the needed functions   #
# for the client to work as either a client or a server #
# respectively.                                         #
#########################################################

import threading
import ConfigParser
import signal
from initialization_client import *

def signal_handler(sig, frame):
 print("Exiting")
 client.stop()
 client.join()
 sys.exit(0)

if __name__=="__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        parser =  ConfigParser.ConfigParser()
        parser.read('config.ini')
        HOST_MANAGER = parser.get('Settings', 'host_manager')
        PORT_MANAGER = int(parser.get('Settings', 'port_manager'))
        client = SocketClient(HOST_MANAGER,PORT_MANAGER)
        client.daemon = True
        client.start()

        ct = 0
        done = False

        while not done:
            if(client.is_alive()):
            #if(True):
                #Counter used just for esthetic purposes in the message presentation
                if(ct == 0):
                    message = raw_input()
                else:
                    message = raw_input("Enter command: \n")
                ct += 1

                if(message == 'Disconnect'):
                    break
                elif(message == 'Pair'):
                    try:
                        client.close()
                        done = pairClient()
                        break
                    except:
                        raise
                        break
            else:
                break
    except:
        pass
