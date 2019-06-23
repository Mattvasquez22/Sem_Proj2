#########################################################
# Script used to initialize server and constrain the    #
# number of possible incoming connections. Every client #
# is handled in a independent connection.               #
#########################################################

import socket
import select
from threading import Thread
from threading import BoundedSemaphore,Semaphore
from connection_char import *
from campaign_sel import *
from find_pair import *

class SocketServer(Thread):
    def __init__(self,host,port,max_clients):
        #Initialize the server.
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET,  socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.sock.bind((host,port))
        #Up to five connections allowed to be queued, standard value
        self.sock.listen(5)
        #Threads registry
        self.sock_threads = []
        #Clients registry
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

        if(self.sock):
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

            if(client_sock):
                client_thr = SocketServerThread(client_sock, client_addr, self.semaph)
                self.sock_threads.append(client_thr)
                #Dictionary needed to keep track of active threads
                THREADS[client_thr.client_ID] = client_thr
                #Dictionary of semaphores needed to lock threads respectively
                SEMAPHORES[client_thr.client_ID] = Semaphore()
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
        self.client_sock.send("Welcome to manager!")
        #check for timestamp, clasify and characterize
        classifyConnection(self.client_ID)
        #print("Pool is: {}".format(POOL))
        self.__stop = False
        while not self.__stop:
            if(self.client_sock):
                #Check if the client is still connected and if data is available:
                try:
                    rdy_read, rdy_write, sock_err = select.select([self.client_sock,], [self.client_sock,], [], 5)
                except select.error as err:
                    print("[Thr {}] Select() failed on socket with {}".format(self.number,self.client_addr))
                    self.close()
                    return

                if(len(rdy_read) > 0):
                    SEMAPHORES[self.client_ID].acquire()
                    try:
                        rdy_read2, rdy_write, sock_err = select.select([self.client_sock,], [], [], 5)
                    except select.error as err:
                        self.close()
                        return
                    if(len(rdy_read2) == 0):
                        self.close()
                        return

                    read_data =  self.client_sock.recv(255)
                    SEMAPHORES[self.client_ID].release()
                    if(len(read_data) == 0):
                        self.stop()
                    #Checks for pair request, finds pair and sends information
                    if(read_data.rstrip() == "Pair"):
                        print("Request for a pair issued by client: {}".format(self.client_ID))
                        removefromPool(self.client_ID)
                        campaignSelection(self)
                        #Pairing up:
                        serv,clnt = findPair(self)
                        if(serv and clnt):
                            try:
                                SEMAPHORES[serv].acquire()
                                #Send to the client_server the id of the client
                                THREADS[serv].client_sock.sendall("Server-{}".format(THREADS[clnt].client_ID))
                                #Receive the port
                                ports = THREADS[serv].client_sock.recv(255)
                                if(ports != 'fail'):
                                    client_serv_tcp_port = ports.split('-')[0]
                                    client_serv_udp_port = ports.split('-')[1]
                                    THREADS[clnt].client_sock.send(ports)
                                    THREADS[clnt].client_sock.send(THREADS[serv].client_ID.split(":")[0])
                                    print("Pairing finished")
                                else:
                                    print('Error with client server')
                                    SEMAPHORES[serv].release()
                                    self.close()
                                    return
                            except:
                                SEMAPHORES[serv].release()
                            SEMAPHORES[serv].release()
                        else:
                            print("Pair not found")
                            self.client_sock.send('Nope')
                            self.close()
                            print("[Connection closed for client {}] with thread {}".format(self.client_ID, self.number))
                            return
            else:
                print("[Thr {}] No client is connected, SocketServer can't receive data".format(self.number))
                self.stop()
        self.close()


    def stop(self):
        self.__stop = True

    def close(self):
        #Close connection with the client socket"
        self.number.release()
        if(self.client_sock):
            #Remove client from the pool
            if(self.client_ID in POOL):
                removefromPool(self.client_ID)     
                THREADS.pop(self.client_ID) 
            self.client_sock.close()


THREADS = {}
SEMAPHORES = {}
