#!/usr/bin/python
#Client code:

import socket
import pickle

def desired_campaigns():
    return ['1','2','3']

if __name__=="__main__":
    host = socket.gethostname()
    port = 33000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    s.connect((host,port))
    req = raw_input()
    s.send(req)    
    data =  pickle.loads(s.recv(1024))
    print(data)
    choices = pickle.dumps(desired_campaigns(),-1)
    s.send(choices) 
    data = s.recv(1024)
    print(data)
