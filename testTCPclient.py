#!/usr/bin/env python

import socket


TCP_IP = '192.168.0.8'
TCP_PORT = 8888
BUFFER_SIZE = 1024

def sendMessage(s, message):
    s.send(message.encode())
    data = s.recv(BUFFER_SIZE)
    print ("received data 1:", data.decode())


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

sendMessage(s, "Hello world")
sendMessage(s, "systemPower")
sendMessage(s, "emergencyStop")
sendMessage(s, "openDoors")
sendMessage(s, "closeDoors")
sendMessage(s, "openRoof")
sendMessage(s, "closeRoof")
sendMessage(s, "extendPad")
sendMessage(s, "retractPad")
sendMessage(s, "raisePad")
sendMessage(s, "lowerPad")
sendMessage(s, "systemStatus")
sendMessage(s, "Connection Test")

s.close()

