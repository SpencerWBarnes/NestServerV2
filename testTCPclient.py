#!/usr/bin/env python

import socket


TCP_IP = '192.168.0.8'
TCP_PORT = 8888
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE.encode())
data = s.recv(BUFFER_SIZE)
print ("received data 1:", data)

s.send(MESSAGE.encode())
data = s.recv(BUFFER_SIZE)
print ("received data 2:", data)

s.send(MESSAGE.encode())
data = s.recv(BUFFER_SIZE)
print ("received data 3:", data)

s.close()

