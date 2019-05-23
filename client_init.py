#########################################################
# Script used to initialize the client when it becomes  #
# a server. Threds implemented in order to handle both  #
# of the cases.                                         #
#########################################################

import socket
import select
import sys
import ConfigParser
from threading import Thread
from threading import BoundedSemaphore

parser = ConfigParser.ConfigParser()
parser.read('config.ini')
HOST_MANAGER = parser.get('Settings', 'host_manager')
PORT_MANAGER = int(parser.get('Settings', 'port_manager'))
HOST_CLIENT_SERVER = parser.get('Settings', 'host_client_server')
PORT_CLIENT_SERVER = int(parser.get('Settings', 'port_client_server'))

def connectClientServ(host,port):
    print("I will connect to {} in port {}".format(host,port))


def pairClient():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.connect((HOST_MANAGER,PORT_MANAGER))
    greeting = sock.recv(42)
    print(greeting)

    while sock:
        sock.send("Pair")
        data = sock.recv(255)
        print("Campaigns are: " + data)
        sock.send('4')
        sock.send('1')
        data = sock.recv(4)
        print(data)
        if(data != "Nope"):
            pair_serv_port = data
            pair_serv_ip = sock.recv(255)
            print("server port is: {}".format(pair_serv_port))
            print("server ip   is: {}".format(pair_serv_ip))
            #print("GO PAIR WIH SERVER")
            connectClientServ(pair_serv_ip,pair_serv_port)
            break
        else:
            print("Pair not found")
            return

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

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
        for thr in self.sock_threads:
            thr.stop()
            thr.join()

        if(self.sock):
            self.sock.close()
            self.sock = None

    def run(self):
        self.__stop = False
        a = self.sock.recv(42)
        print(a)
        while not self.__stop:
            if(self.sock):
                try:
                    rdy_read, rdy_write, sock_err = select.select([self.sock,], [self.sock,], [], 5)        
                except select.error as err:
                    print('stop')
                    self.stop()
                    return
            
            if(len(rdy_read) > 0):
                read_data = self.sock.recv(255)
                print("DATA READ IS: " + read_data)
                if("Server" in read_data):
                    print("Become a server!")
                    self.sock.send(str(PORT_CLIENT_SERVER))
                    print('port sent: '+ str(PORT_CLIENT_SERVER))
                    client_info = read_data.split('-')[1]
                    client_ip = client_info.split(':')[0]
                    print("received: " + client_ip)
                    print("START LISTENING")
                    break
                    #client_server = SocketServer(HOST,int(PORT_S)) 
                    #client_server.start()
                    #self.close()
                self.stop()
        #print('chiuso')
        self.close() 

    def stop(self):
        self.__stop = True

class SocketServer(Thread):
    def __init__(self,host,port):
        #Initialize the client_server
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.host = host
        self.port = port
        self.sock.bind((host,port))
        self.sock.listen(1)
        self.sock_threads = []

    def close(self):
        #Close the threads
        for thr in self.sock_threads:
            thr.stop()
            thr.join()

        if(self.sock):
            self.sock.close()
            self.sock = None

    def run(self):
        #Accept incoming connection
        self.__stop = False
        while not self.__stop:
            self.sock.settimeout(1)
            try:
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                client_sock = None

            if(client_sock):
                client_thread = ClientServerThread(client_sock,client_addr)
                self.sock_threads.append(client_thr)
                client_thr.start()
        self.close()

    def stop(self):
        self.__stop = True

def ClientServerThread(Thread):
    def __init__(self,client_sock,client_addr,number):
        #Initialize the thread with a client socket and address
        Thread.__init__(self)
        self.client_sock = client_sock
        self.client_addr = client_addr
        #Optional
        self.number = number

    def run(self):
        self.__stop = False
        print("Client server online!")
        while not self.__stop:
            if(self.client_sock):
            #Check if the client is still connected and if data is available
                try:
                    rdy_read, rdy_write, sock_err = select.select([self.client_sock,], [self.client_sock,], [], 5)
                except select.error as err:
                    print("[Thr {}] Select() failed on socket with {}".format(self.number,self.client_addr))
                    self.stop()
                    return

                if(len(rdy_read) > 0):
                    read_data = self.client_sock.recv(255)
                    #Check if socket has been closed
                    if(len(read_data) == 0):
                        print("[Connection closed for client {}] with thread {}".format(self.client_ID, self.number))
                        self.stop()
                    elif(read_data.rstrip() == "Disconnect"):
                        self.stop()
                    print("Data recv is: {}".format(read_data.rstrip()))

            else:
                print("[Thr {}] No client is connected, SocketServer can't receive data".format(self.number))
                self.stop()
        self.close()

    def stop(self):
        self.__stop = True

    def close(self):
        if(self.client_sock):
            self.client_sock.close()

