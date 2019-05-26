#########################################################
# Script used to manage the connection and pairing of   #
# the client with the manager, as well as import other  #
# scripts to specify the start of the campaign.         #
#########################################################

import ConfigParser
from server_camp import *
from client_camp import *

parser = ConfigParser.ConfigParser()
parser.read('config.ini')
HOST_MANAGER = parser.get('Settings', 'host_manager')
PORT_MANAGER = int(parser.get('Settings', 'port_manager'))
HOST_CLIENT_SERVER = parser.get('Settings', 'host_client_server')
PORT_CLIENT_SERVER = int(parser.get('Settings', 'port_client_server'))

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
        data = sock.recv(255)
        print('data is ' + data)
        if(data != "Nope"):
            pair_serv_port = data[:4]
            pair_serv_ip = sock.recv(255)
            print("server port is: {}".format(pair_serv_port))
            print("server ip   is: {}".format(pair_serv_ip))
            #sock.close()
            startCampaign(pair_serv_ip,pair_serv_port)
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
                    #try:
                    self.sock.send(str(PORT_CLIENT_SERVER))
                    print('port sent: '+ str(PORT_CLIENT_SERVER))
                    #except:
                    #print('not sent')

                    client_info = read_data.split('-')[1]
                    client_ip = client_info.split(':')[0]
                    print("received: " + client_ip)
                    print("START LISTENING")
                    client_server = SocketServer(HOST_CLIENT_SERVER,PORT_CLIENT_SERVER,1)
                    client_server.daemon = True
                    client_server.start()
                    break
                    #client_server = SocketServer(HOST,int(PORT_S)) 
                    #client_server.start()
                    #self.close()
                self.stop()
        self.close() 

    def stop(self):
        self.__stop = True

#
