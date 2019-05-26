#########################################################
# Script used to specify the start of the campaign from #
# the client_server side.								#
#########################################################


import socket
import select
import sys
from threading import Thread
from threading import BoundedSemaphore

class SocketServer(Thread):
    def __init__(self,host,port,max_clients):
        #Initialize the client_server
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.host = host
        self.port = port
        self.sock.bind((host,port))
        self.sock.listen(3)
        self.sock_threads = []
        self.semaph = BoundedSemaphore(value=max_clients)

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
                self.semaph.acquire()
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                client_sock = None

            if(client_sock):
                client_thread = ClientServerThread(client_sock, client_addr, self.semaph)
                self.sock_threads.append(client_thread)
                client_thread.start()
            else:
                self.semaph.release()
        self.close()

    def stop(self):
        self.__stop = True

class ClientServerThread(Thread):
    def __init__(self, client_sock, client_addr, number):
        #Initialize the thread with a client socket and address
        Thread.__init__(self)
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.client_ID = client_addr[0] + ":" + str(client_addr[1])
        self.number = number

    def run(self):
        self.__stop = False
        print("Client server online!")
        self.client_sock.send("Welcome to the client_server")
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
                    #print("Data recv is: {}".format(read_data.rstrip()))
                    #Check if socket has been closed
                    if(len(read_data) > 0):
                        print("Data recv is: {}".format(read_data.rstrip()))
                        #print("[Connection closed for client {}] with thread {}".format(self.client_ID, self.number))
                        #self.stop()
                    if(read_data.rstrip() == "Disconnect"):
                        self.stop()

            else:
                print("[Thr {}] No client is connected, SocketServer can't receive data".format(self.number))
                self.stop()
        self.close()

    def stop(self):
        self.__stop = True

    def close(self):
        self.number.release()
        if(self.client_sock):
            self.client_sock.close()

