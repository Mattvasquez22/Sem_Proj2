#!/usr/bin/python
#Manager code

import socket
import thread
import pickle

def get_campaigns():
    camps = {'a':1,'b':2}
    return camps
def place_in_pool(addr):
    pool = []
    pool.append(addr)
    print("Current pool is: " + str(pool))

def characterize_client(addr):
    print("Client: " + addr + " has been characterized")

def new_client(clientsocket,addr):
    while True:
        msg =  clientsocket.recv(1024)
        #characterize_client(addr[0])
        #place_in_pool(addr[0])
        if(msg == 'pair'):
            campaings = pickle.dumps(get_campaigns(),-1)
            clientsocket.send(campaings)
            desired_camp =  pickle.loads(clientsocket.recv(1024))
            print(desired_camp)
            clientsocket.send("Finding pair")
        #msg =  raw_input('Server: ')
        #clientsocket.send(msg)
    clientsocket.close()


if __name__=="__main__":
    s = socket.socket()
    host = socket.gethostname()
    port = 33000
    print "Manager online!"
    s.bind((host,port))
    s.listen(5)
    while True:
        c, addr = s.accept()
        #print(addr)
        print("New client from: " + addr[0])
        thread.start_new_thread(new_client,(c,addr))
        characterize_client(addr[0])
        place_in_pool(addr[0])

    s.close()
