#########################################################
# Script used to manage the connection and pairing of   #
# the client with the manager, as well as import other  #
# scripts to specify the start of the campaign.         #
#########################################################

import ConfigParser
import select
import sys
from threading import Thread,Semaphore
from server_camp import *
from client_camp import *

parser = ConfigParser.ConfigParser()
parser.read('config.ini')
HOST_MANAGER = parser.get('Settings', 'host_manager')
PORT_MANAGER = int(parser.get('Settings', 'port_manager'))
HOST_CLIENT_SERVER = parser.get('Settings', 'host_client_server')
TCP_PORT_CLIENT_SERVER = int(parser.get('Settings', 'tcp_port_client_server'))
UDP_PORT_CLIENT_SERVER = int(parser.get('Settings', 'udp_port_client_server'))

def pairClient():
    #Connection to manager
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.connect((HOST_MANAGER,PORT_MANAGER))
    greeting = sock.recv(42)
    print(greeting)
    while sock:
        sock.send("Pair")
        data = sock.recv(255)
        #Campaign selection
        print("Campaigns are: " + data)
        sock.send('1')
        data = sock.recv(255)
        if(data != "Nope" and len(data) != 0):
            #Receive ports of new server
            client_serv_tcp_port = int(data.split('-')[0])
            client_serv_udp_port = int(data.split('-')[1])
            #Receive ip of new server
            pair_serv_ip = sock.recv(255)
            clientCampaign(pair_serv_ip,client_serv_tcp_port,client_serv_udp_port)
        else:
            print("Pair not found")
            return False

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    return True

class SocketClient(Thread):
    def __init__(self,host,port):
        #Initialize the client
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.host = host
        self.port = port
        self.sock.connect((host,port))
        self.sock_threads = []
        
    def close(self):
        if(self.sock):
            self.sock.close()
            self.sock = None

    def run(self):
        self.__stop = False
        greeting = self.sock.recv(42)
        print(greeting)
        while not self.__stop:
            if(self.sock):
                try:
                    rdy_read, rdy_write, sock_err = select.select([self.sock,], [self.sock,], [], 5)        
                except select.error as err:
                    self.stop()
                    return
            
            if(len(rdy_read) > 0):
                #Message received from manager
                read_data = self.sock.recv(255)
                print('read data is {}'.format(read_data))
                if("Server" in read_data):
                    print("Become a server!")
                    s,lstn_flag = startListen(HOST_CLIENT_SERVER,TCP_PORT_CLIENT_SERVER)
                    #Check if new server is ready
                    if(lstn_flag):
                        print('Server is listening')
                        ports = '{}-{}'.format(TCP_PORT_CLIENT_SERVER,UDP_PORT_CLIENT_SERVER)
                        self.sock.sendall(ports)
                        self.close()
                        client_info = read_data.split('-')[1]
                        client_ip = client_info.split(':')[0]
                        print('Start campaing')
                        serverCampaign(s,client_ip)
                        break
                    else:
                        self.sock.sendall('fail')
                        print('Server failed to start')
                        break
                self.stop()
        self.close() 

    def stop(self):
        self.__stop = True

