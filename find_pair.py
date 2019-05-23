#########################################################
# Script used to define the functions used to look for  #
# an appropriate pair in the POOL when requested, as    #
# well as managing the case where no pair was found     #
#########################################################

from connection_char import placeinPool,removefromPool,POOL,TIMESTAMPS
#from connection_char import *

def findPair(client):
    if(len(POOL) < 1):
        server_pair = False
    else:
        #Find pair:
        server_pair = POOL.keys()[0]
    if(server_pair):
        print("PAIR FOUND IS {}".format(server_pair))
        #remove server found from pool
        removefromPool(server_pair)
        return server_pair,client.client_ID
    else:
        #placeinPool(client.client_ID,TIMESTAMPS[client.client_ID])
        return None,None
