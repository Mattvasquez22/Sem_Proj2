#############################################################
# Script used to specify the campaign for the client. It    #
# will ping the host, connect to it using TCP to a port     #
# given by the server, send a UDP packet to another port    # 
# given by the server, and receive the connections feedback #
#############################################################

import os
import socket
import sys

def pingHost(host):
    #If want to hide ping response
    #resp = os.system('ping -c 1 ' + host + ' > /dev/null 2>&1')
    resp = os.system('ping -c 1 ' + host)
    if(resp == 0):
        return True
    else:
        return False

def connectTCP(HOST,TCP_PORT):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST,TCP_PORT))
        return sock 
    except:
        return False

def connectUDP(HOST,UDP_PORT):
    message = 'Test'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message, (HOST, UDP_PORT))
        report,addr = sock.recvfrom(1024)
        print("[-] Report: {}".format(report))
    except:
        print("[!] Failed in UDP connection")
        raise
        return

def clientCampaign(HOST,TCP_PORT,UDP_PORT):
    print("[+] Connecting to server")
    sock_TCP = connectTCP(HOST,TCP_PORT)
    #Stablish TCP connection
    if(sock_TCP == False):
        print("[!] Failed to connect to server, exiting")
        sys.exit(0)
    print('[+] Connected')
    #Initialization check
    message = 'Ready to start campaign'
    sock_TCP.sendall(message)
    print("[+] {}".format(message))
    response = sock_TCP.recv(255)
    print('[-] {}'.format(response))
    
    #Stablish UDP connection
    message = 'Going to send a UDP packet, ready?'
    sock_TCP.sendall(message)
    print("[+] {}".format(message))
    response = sock_TCP.recv(255)
    print('[-] {}'.format(response))
    if(response == 'yes'):
        connectUDP(HOST,UDP_PORT)
    else:
        print('[+] Server not ready to receive UDP packets')
    sock_TCP.shutdown(socket.SHUT_RDWR) 
    sock_TCP.close()
    sys.exit(0)
