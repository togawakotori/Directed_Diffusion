#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 19 13:35:20 2018

@author: longzhan
"""

import socket
import threading
import time
# 报文格式：
# 兴趣：int + nodeID(目标点，1位) + intID(3位) + interval(4位) + exp(2位) example:int2001000520
# 数据：dat + nodeID(来源点，1位) + intID(3位) + interval(4位) + dataID(3位) + data
nodeID = 0
neighbour = [('192.168.137.193',7773)]

intCache = {} # intID:([interval], exp, tgt)
dataCache = {} # intID:[dataID]
threadID = 3

def num2str(num, size):
    num = str(num)
    l = len(num)
    for i in range(size-l):
        num = '0' + num
    return num

class server(threading.Thread):
    def __init__(self, threadID, name, addr, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.addr = addr
        self.port = port
    def run(self):
        global threadID
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.addr, self.port))
        serversocket.listen(5)
        while True:
            clientsocket,addr = serversocket.accept()   
            ip = addr[0]
            index = 0 #数据来源
            for i in range(len(neighbour)):
                if ip == neighbour[i][0]:
                    index = i
            msg = clientsocket.recv(1024)
            msg = msg.decode('utf8')
            if msg[:3] == 'dat':
                tgt = msg[3]
                intID = msg[4:7]
                dataID = msg[11:14]
                data = msg[14:]
                if intID in intCache:
                    if len(intCache[intID][0]) == 1: #第一个收到的数据包
                        org_interval = intCache[intID][0][0]
                        new_interval = int(org_interval) * 2
                        intCache[intID][0].append(num2str(new_interval,4))
                        dataCache[intID] = [dataID]
                        print(data)
                        #增强
                        msg = 'int' + tgt + intID + \
                            num2str(new_interval,4) + intCache[intID][1] 
                        thread3 = send(threadID, 'client'+str(threadID), 
                                         neighbour[index][0], neighbour[index][1], msg)
                        thread3.start()
                        threadID += 1
                        print('增强报文发出:', msg)
                    elif dataID not in dataCache[intID]:
                        dataCache[intID].append(dataID)
                        print(data)
                    else:
                        pass
            clientsocket.close()

class send(threading.Thread):
    def __init__(self, threadID, name, addr, port, msg, delay=0):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.addr = addr
        self.port = port
        self.msg = msg
        self.delay = delay
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.addr, self.port))
        except:
            print("Connection to " + self.addr + "failed")
        time.sleep(self.delay)
        s.send(self.msg.encode('utf-8'))
        s.close()
    
class client(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        global threadID
        while True:
            msg = input()
            msg = msg[:len(msg)-2] + str(int(time.time())+int(msg[len(msg)-2:len(msg)]))
            tgt = msg[3]
            intID = msg[4:7]
            interval = msg[7:11]
            expire = msg[11:]
            intCache[intID] = ([interval], expire, tgt)
            for i in range(len(neighbour)):
                addr = neighbour[i][0]
                port = neighbour[i][1]
                thread4 = send(threadID, 'client'+str(threadID), addr, port, msg)
                thread4.start()
                threadID += 1
                

thread1 = server(1, 'server1', '', 7770)
thread2 = client(2, 'client1')

thread1.start()
thread2.start()

thread2.join()
thread1.join()