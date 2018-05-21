#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 19 13:35:20 2018

@author: longzhan
"""

import socket
import threading

# 报文格式：
# 兴趣：int + nodeID + others
# 数据：dat + nodeID + 数据
nodeID = 0

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
                pass
            else:
                print(msg)
            clientsocket.close()
            
class client(threading.Thread):
    def __init__(self, threadID, name, addr, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.addr = addr
        self.port = port
    def run(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            msg = input()
            s.connect((self.addr, self.port))
            s.send(msg.encode('utf-8'))
            s.close()

thread1 = server(1, 'server1', '127.0.0.1', 7769)
thread2 = client(2, 'client1', '127.0.0.1', 7770)

thread1.start()
thread2.start()

thread2.join()
thread1.join()