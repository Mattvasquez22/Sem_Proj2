#########################################################
# Script used to specify the start of the campaign from #
# the client side.										#
#########################################################

import socket

def startCampaign(pair_host,pair_port):
    print("I will connect to {} in port {}".format(pair_host,pair_port))
    sock_p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_p.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock_p.connect((pair_host,int(pair_port)))
    greet = sock_p.recv(42)
    print(greet)
    sock_p.send('sono arrivato')

