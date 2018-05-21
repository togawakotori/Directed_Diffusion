#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 19 13:39:29 2018

@author: longzhan
"""

import socket
import threading

nodeID = 1 #注意改动
class server(threading.Thread):
    def __init__(self, threadID, name, addr, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.addr = addr
        self.port = port
    def run(self):
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.addr, self.port))
        serversocket.listen(5)
        while True:
            clientsocket,addr = serversocket.accept()      
            msg = clientsocket.recv(1024)
            msg = msg.decode('utf8')
            if msg[:3] == 'int':
                if int(msg[3]) == nodeID:
                    print('Recived:',msg)
                    msg = 'dat' + str(nodeID) + 'temp36'
                    #注意改动
                    thread3 = client(3, 'client3', '127.0.0.1', 7769, msg)
                    thread3.start()                    
                else:
                    #注意改动
                    thread2 = client(2, 'client1', '127.0.0.1', 7771, msg)
                    thread2.start()                   
            else:
                #注意改动
                thread3 = client(2, 'client2', '127.0.0.1', 7769, msg)
                thread3.start()
            clientsocket.close()
            
class client(threading.Thread):
    def __init__(self, threadID, name, addr, port, msg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.addr = addr
        self.port = port
        self.msg = msg
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.addr, self.port))
        s.send(self.msg.encode('utf-8'))
        s.close()

thread1 = server(1, 'server1', '127.0.0.1', 7770) #注意改动

thread1.start()

thread1.join()