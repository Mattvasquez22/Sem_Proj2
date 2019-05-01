#########################################################
# Script used to initialize server and constrain the    #
# number of possible incoming connections. Every client #
# is handled in a independent connection.               #
#########################################################
import socket
import select
from threading import Thread
from threading import BoundedSemaphore
from conn_char import *

class SocketServer(Thread):
    def __init__(self, host, port, max_clients):
        #Initialize the server.
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET,  socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.sock.bind((host,port))
        #Up to five connections allowed to be queued, standard value
        self.sock.listen(5)
        #Pool for the clients, data structure yet to be defined
        self.sock_threads = []
        self.sock_pool = POOL
        #Timestam registry
        self.sock_timestamp = TIMESTAMPS
        #Semaphores used to constrain the possible connections 
        self.semaph = BoundedSemaphore(value=max_clients)

    def close(self):
        #Close the client threads and server socket if they exist.
        print("Manager offline")
        for thr in self.sock_threads:
            thr.stop()
            thr.join()

        if self.sock:
            self.sock.close()
            self.sock = None

    def run(self):
        #Accept an incoming connection
        print("Manager online from: {}, port: {}".format(self.host,self.port))
        self.__stop = False
        while not self.__stop:
            self.sock.settimeout(1)
            try:
                self.semaph.acquire()
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                client_sock = None

            if client_sock:
                client_thr = SocketServerThread(client_sock, client_addr, self.semaph)
                self.sock_threads.append(client_thr)
                client_thr.start()
            else:
                self.semaph.release()
        self.close()
    
    def stop(self):
        self.__stop = True


class SocketServerThread(Thread):
    def __init__(self, client_sock, client_addr, number):
        #Initialize the thread with a client socket and address
        Thread.__init__(self)
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.client_ID = client_addr[0] + ":" + str(client_addr[1])
        self.number = number

    def run(self):
        print("[New client {}] started with thread {}".format(self.client_ID, self.number))
        #check for timestamp, clasify and characterize
        classifyConnection(self.client_ID)
        self.__stop = False
        while not self.__stop:
                if self.client_sock:
                    #Check if the client is still connected and if data is available:
                    try:
                        rdy_read, rdy_write, sock_err = select.select([self.client_sock,], [self.client_sock,], [], 5)
                    except select.error as err:
                        print("[Thr {}] Select() failed on socket with {}".format(self.number,self.client_addr))
                        self.stop()
                        return

                    if(len(rdy_read) > 0):
                        read_data =  self.client_sock.recv(255)
                        #Check if socket has been closed
                        if(len(read_data) == 0):
                            print("[Connection closed for client {}] with thread {}".format(self.client_ID, self.number))
                            self.stop()
                        #Checks for disconnect message
                        elif(read_data.rstrip() == "Disconnect"):
                            self.stop()
                        else:
                            #Strip newlines for output clarity
                            print('[Received from client {} with thread {}] {}'.format(self.client_ID, self.number, read_data.rstrip()))

                else:
                    print("[Thr {}] No client is connected, SocketServer can't receive data".format(self.number))
                    self.stop()
        self.close()

    def stop(self):
        self.__stop = True

    def close(self):
        #Close connection with the client socket"
        self.number.release()
        if self.client_sock:
            print("[Closing connection for client {}] with thread {}".format(self.client_ID, self.number))
            #Remove client from the pool
            removefromPool(self.client_ID)      
            self.client_sock.close()

