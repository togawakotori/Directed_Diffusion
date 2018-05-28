#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 19 13:49:40 2018

@author: longzhan
"""

import socket
import threading
import time
import RPi.GPIO as GPIO
# 报文格式：
# 兴趣：int + nodeID(目标点，1位) + intID(3位) + interval(4位) + exp(2位)
# 数据：dat + nodeID(来源点，1位) + intID(3位) + interval(4位) + dataID(3位) + data

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
R = 11
G = 12
B = 13

def setup(Rpin, Gpin, Bpin):
	global pins
	global p_R, p_G, p_B
	pins = {'pin_R': Rpin, 'pin_G': Gpin, 'pin_B': Bpin}
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	for i in pins:
		GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
		GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
	
	p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
	p_G = GPIO.PWM(pins['pin_G'], 1999)
	p_B = GPIO.PWM(pins['pin_B'], 5000)
	
	p_R.start(0)      # Initial duty Cycle = 0(leds off)
	p_G.start(0)
	p_B.start(0)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def off():
	for i in pins:
		GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds

def setColor(col):   # For example : col = 0x112233
	R_val = (col & 0xff0000) >> 16
	G_val = (col & 0x00ff00) >> 8
	B_val = (col & 0x0000ff) >> 0

	R_val = map(R_val, 0, 255, 0, 100)
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)
	
	p_R.ChangeDutyCycle(100-R_val)     # Change duty cycle
	p_G.ChangeDutyCycle(100-G_val)
	p_B.ChangeDutyCycle(100-B_val)

def destroy():
	p_R.stop()
	p_G.stop()
	p_B.stop()
	off()
	GPIO.cleanup()
    
nodeID = 3 #注意改动
#注意改动
threadID = 1
neighbour = [('192.168.1.178',7772),
             ('192.168.1.154',7771)]
intCache = {} # intID:(nodeID, [interval], exp, [grad])
dataCache = {} # intID:[dataID]
first = {} # intID:index #第一次接受特定请求返回的数据包的来源
origin_interval = {} # intID:interval
rflag = {} #init:flag
global_delay = 10000 #10/interval
def checkCache(): #删除过期记录
    dellist = []
    for key in intCache:
        if int(time.time()) - int(intCache[key][2]) > 0:
            dellist.append(key)
    for key in dellist:
        if key in intCache:
            del(intCache[key])
        if key in dataCache:
            del(dataCache[key])

def num2str(num, size):
    num = str(num)
    l = len(num)
    for i in range(size-l):
        num = '0' + num
    return num

class broadcast(threading.Thread):
    def __init__(self, threadID, name, intID, expire):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.expire = expire
        self.intID = intID
    def run(self):
        global global_delay
        global threadID
        counter = 0
        #print("now:",int(time.time()))
        #print("expire:",int(self.expire))
        while int(time.time()) - int(self.expire) <= 0: #在过期之前不停发数据
            msg = 'dat' + str(nodeID) + self.intID + num2str(int(10/global_delay),4) + \
                num2str(counter,3) + 'report!'+str(counter)
            counter += 1
            addr = []
            port = []
            for i in range(len(neighbour)):
                addr.append(neighbour[i][0])
                port.append(neighbour[i][1])
            thread3 = client(threadID, 'client'+str(threadID),
                             addr, port, msg)
            threadID += 1
            thread3.start()
            setup(R, G, B)
            setColor(colors[0])
            destroy() 
            time.sleep(global_delay)
            print("Sent datarate:",global_delay)
        global_delay = 10000


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
            msg = clientsocket.recv(1024)
            msg = msg.decode('utf8')
            index = 0 #兴趣报文来源节点
            for i in range(len(neighbour)):
                if neighbour[i][0] == ip:
                    index = i
            if msg[:3] == 'int': #兴趣报文
                tgt = msg[3]
                intID = msg[4:7]
                interval = msg[7:11]
                expire = str(int(time.time())+int(msg[len(msg)-2:len(msg)]))
                checkCache()
                tmp = 10/int(interval)
                global global_delay
                if int(tgt) == nodeID: #命中，返回数据
                    if tmp<global_delay: #总是选最快速率转发
                        global_delay = tmp
                    print('Receive interest message:',msg)
                    if intID not in intCache:
                        thread4 = broadcast(threadID, 'bc', intID, expire)
                        thread4.start()
                        threadID += 1
                        intCache[intID] = (tgt,[interval], expire, [index])
                        origin_interval[intID] = interval
                        rflag[intID] = False
                else: #不命中，需要继续转发
                    print('Receive interest message:',msg)
                    if intID in intCache:
                        if index not in intCache[intID][3]: #增加gradient
                            intCache[intID][3].append(index)
                            intCache[intID][1].append(interval)
                        elif intCache[intID][1][intCache[intID][3].index(index)] != \
                            interval:
                                intCache[intID][1][intCache[intID][3].index(index)] \
                                = interval
                                rflag[intID] = True  #说明当前节点被增强了
                                #print(rflag)
                        else:
                            pass
                    else: #创建新的entry
                        intCache[intID] = (tgt,[interval], expire, [index])
                        origin_interval[intID] = interval
                        rflag[intID] = False
                    if int(time.time()) - int(expire) <= 0:
                        if rflag[intID] == False: #正常转发
                            addr = []
                            port = []
                            for i in range(len(neighbour)):
                                if i not in intCache[intID][3]: #单箭头
                                    addr.append(neighbour[i][0])
                                    port.append(neighbour[i][1])
                            if len(addr) != 0:
                                thread2 = client(threadID, 'client'+str(threadID),
                                                 addr, port, msg)
                                thread2.start()
                                threadID += 1
                        else:
                            #只将增强报文发给一个节点
                            #msg0 = 'int' + tgt + intID + origin_interval[intID] + expire
                            #print(first[intID])
                            for i in range(len(neighbour)):
                                addr = neighbour[i][0]
                                port = neighbour[i][1]
                                if i == first[intID]:
                                    thread2 = client(threadID, 'client'+str(threadID),
                                                     [addr], [port], msg)
                                    threadID += 1
                                    thread2.start()
                                    break
            else:#数据报文
                intID = msg[4:7]
                interval = msg[7:11]
                dataID = msg[11:14]
                if intID in intCache:
                    grad = intCache[intID][3]
                    expInterval = intCache[intID][1]
                    if intID not in dataCache:
                        dataCache[intID] = []
                        first[intID] = index
                    if dataID not in dataCache[intID]:
                        dataCache[intID].append(dataID)
                        for i in range(len(grad)):
                            addr = neighbour[grad[i]][0]
                            port = neighbour[grad[i]][1]
                            #按最大延迟转发
                            delay = max(10/int(expInterval[i]),10/(int(interval)))
                            print('Data Delay to ',i,':',delay)
                            thread3 = client(threadID, 'client'+str(threadID),
                                             [addr], [port], msg, delay)
                            thread3.start()
                                
            clientsocket.close()

class client(threading.Thread):
    def __init__(self, threadID, name, addr, port, msg, delay=0):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.addr = addr
        self.port = port
        self.msg = msg
        self.delay = delay
    def run(self):
        color_index = 0
        if self.msg[:3] == 'int':
            color_index = 1
        for i in range(len(self.addr)):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((self.addr[i], self.port[i]))
            except:
                print("Connection to " + self.addr[i] + "failed")
            time.sleep(self.delay)
            s.send(self.msg.encode('utf-8'))
            s.close()
            #setup(R, G, B)
            #setColor(colors[color_index])
            #destroy()

 
     
thread1 = server(0, 'server', '', 7773) #注意改动
    
thread1.start()
   
thread1.join()
 
