#############################################################
# Script used to specify the campaign for the server. It    #
# will listen to a port specified to the manager, receive   #
# a UDP packet from the client and answer with the feedback # 
# of seen connections, along with the TTL of packets        #  
#############################################################


from scapy.all import AsyncSniffer,IP
import socket
import time
import ConfigParser
import sys

info = ''
def signal_handler(sig, frame):
    print("Exiting client server")
    server.stop()
    server.join()
    sys.exit(0)

def printPacket(pkt):
    global info
    if(IP in pkt):
        ip_ttl = pkt[IP].ttl
        info += "{} / ttl {}\n".format(pkt.summary(),ip_ttl)

def startListen(HOST,PORT):
    ready = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST,PORT))
        s.listen(5)
        print('Server online, listening in: {}:{} '.format(HOST,PORT))
        ready = True
        return  s,ready
    except:
        print('Could not start server')
        return False,ready

def campaign1(s,HOST,TCP_PORT,UDP_PORT,client_ip):
    conn,addr = s.accept()
    conn_ip = addr[0]
    if(conn_ip != client_ip):
        return
    if(conn):
        try:
            sniffer = AsyncSniffer(iface='lo', prn = printPacket, filter='dst port {}'.format(UDP_PORT))
            sniffer.start()
            time.sleep(1)
            #Initialization check:
            check = conn.recv(255)
            print("[-] {}".format(check))
            response = 'yes'
            conn.sendall(response)
            time.sleep(1) 
            #UDP packet:
            request = conn.recv(255)
            print("[-] {}".format(request))
            #Start UDP server
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((HOST,UDP_PORT))
                print('[+] UDP server started')
                response = 'yes'
            except:
                response = 'no'
                raise
            
            try:
                conn.sendall(response) 
                data,address = sock.recvfrom(1024)
                time.sleep(1)
                print('[*] Received: {}'.format(data))
                result = 'Success, report is: \n{}'.format(info)
                sock.sendto(result,address)
                sniffer.stop()
            except:
                result = 'Failed, report is: \n{}'.format(info)
                sock.sendto(result,address)
                sniffer.stop()
        except:
            print('[+] Error connecting to client')
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            raise
    s.shutdown(socket.SHUT_RDWR)
    s.close()

def serverCampaign(s,client_ip):
    #Get ports from config file
    parser = ConfigParser.ConfigParser()
    parser.read('config.ini')
    HOST = parser.get('Settings', 'host_client_server')
    TCP_PORT = int(parser.get('Settings', 'tcp_port_client_server'))
    UDP_PORT = int(parser.get('Settings', 'udp_port_client_server'))
    campaign1(s,HOST,TCP_PORT,UDP_PORT,client_ip)

