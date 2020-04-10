#!/usr/bin/env python

import socket
import StringConstants as strings


TCP_IP = '192.168.0.8'
TCP_PORT = 8888
BUFFER_SIZE = 1024

def sendMessage(s, message):
    s.sendall(message.encode())
    data = s.recv(BUFFER_SIZE)
    print ("received data 1:", data.decode())


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

sendMessage(s, "Hello world")
sendMessage(s, strings.MESSAGE_SYSTEM_POWER)
sendMessage(s, strings.MESSAGE_EMERGENCY_STOP)
sendMessage(s, strings.MESSAGE_OPEN_DOORS)
sendMessage(s, strings.MESSAGE_CLOSE_DOORS)
sendMessage(s, strings.MESSAGE_OPEN_ROOF)
sendMessage(s, strings.MESSAGE_CLOSE_ROOF)
sendMessage(s, strings.MESSAGE_EXTEND_PAD)
sendMessage(s, strings.MESSAGE_RETRACT_PAD)
sendMessage(s, strings.MESSAGE_RAISE_PAD)
sendMessage(s, strings.MESSAGE_LOWER_PAD)
sendMessage(s, strings.MESSAGE_SYSTEM_STATUS)
sendMessage(s, strings.MESSAGE_CONNECTION_TEST)

s.close()

