'''Author: Lily S.
    I made this simple UDP server then added a GUI to it.
    Still a work in progress but it does speak to the client
    and return a message'''

import socket
import sys
import time
import threading
import json
from PlcClient import PlcClient, PlcClientDev #TODO: remove dev

# default values for IP and Port (IPV4 on Windows, en0 on OSX)
UDP_IP_ADDRESS = '192.168.0.8'
UDP_CLIENT_PORT_NUM = 8000

# Error messages: The error prefix is relevant because it is how the clients know when an error has occured.count
#                 They parse the error prefix to get error messages. The error dictionary represents different states
#                 that can occur within the nest. 
ERROR_PREFIX = "Error: "
errorDictionary = {
            "unknownMessage" : "Unknown Message",
            "isOn" : "Must turn system off",
            "isOff" : "Must turn system on",
            "doorsAreOpen" : "Must close doors",
            "doorsAreClosed" : "Must open doors",
            "roofIsOpen" : "Must close roof",
            "roofIsClosed" : "Must open roof",
            "padIsExtended" : "Must retract pad",
            "padIsRetracted" : "Must extend pad",
            "padIsRaised" : "Must lower pad",
            "padIsLowered" : "Must raise pad",
            "isStopped" : "Must restart system",
            "isStarted" : "Must stop system"
        }

## TODO: check if isOn and isStopped are different>

# This is a guiless server. It runs in the background in pyfladesklocal.py
class Server():
    def __init__(self, parent=None):
        
        # States
        self.running = True
        self.isOn = False
        self.isDoorOpen = False
        self.isRoofOpen = False
        self.isPadExtended = False
        self.isPadRaised = False
        self.isStopped = False
        self.isConnected = False

        # messagetext: holds the value of the message to be sent to the client
        self.messagetext = None

        # PlcClient
        self.plc = PlcClient()          # This is for production mode
        # self.plc = PlcClientDev()     # This is for development mode. It makes a client with empty functions
        self.plc.initButtons()          # Gets button information from the PlcClient browser window

        # connectThread: setting the daemon attribute to True makes it so that when the main thread is exited, so is this thread
        self.connectThread = threading.Thread(target=self.connection)
        self.connectThread.daemon = True
        
        # sockets
        self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        #Port: 8000

    # serverCallback is a function that should be overridden in pyfladesklocal.py in order to update the server's UI
    def serverCallback(self):
        print("serverCallback: you should override this")

    # closeSocket is run when the server is taken down to ensure that the socket is closed. 
    # This usually throws the exception, but I have this function called just in case.
    def closeSocket(self, mSocket):
        try:
            mSocket.shutdown(socket.SHUT_RDWR)
            mSocket.close()
        except Exception as e: # This is usually thrown, but that's okay. 
            print("Server.closeSocket exception: " + str(e))

    # This function closes all sockets in the program. We used to have more, but now all we have is commandSock
    def closeSockets(self):
        self.running = False
        self.closeSocket(self.commandSock)

    # When the gui is closed, close the plc browser and all the sockets     
    def closeEvent(self):
        self.plc.close()
        self.closeSockets()

    def unknownMessage(self, addr):
        self.messagetext = ERROR_PREFIX + errorDictionary['unknownMessage']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def systemStatus(self, addr):
        systemStatusDict = {
            "isOn" : self.isOn,
            "isDoorOpen" : self.isDoorOpen,
            "isRoofOpen" : self.isRoofOpen,
            "isPadExtended" : self.isPadExtended,
            "isPadRaised" : self.isPadRaised,
            "isStopped" : self.isStopped,
            "previousCommand" : self.messagetext
        }
        message = json.dumps(systemStatusDict)
        print(message)
        self.commandSock.sendto(message.encode(), addr)

    def getSystemStatusDict(self):
        systemStatusDict = {
            "isOn" : self.isOn,
            "isDoorOpen" : self.isDoorOpen,
            "isRoofOpen" : self.isRoofOpen,
            "isPadExtended" : self.isPadExtended,
            "isPadRaised" : self.isPadRaised,
            "isStopped" : self.isStopped,
            "previousCommand" : self.messagetext
        }
        return systemStatusDict

    def systemPower(self, addr):
        # this is where the mechanism for powering on and off the system will go
        # for now it will be just a message to the client that the system has been powered on or off
        # I want it to test if the system is on or off first then power it on or off then test again and send the result
        # of the last test
        if self.isOn:
            if self.isDoorOpen or self.isRoofOpen:
                self.messagetext = ERROR_PREFIX
                if self.isDoorOpen:
                    self.messagetext = self.messagetext + errorDictionary['doorsAreOpen']
                if self.isRoofOpen:
                    self.messagetext = self.messagetext + errorDictionary['roofIsOpen']
            else:
                self.messagetext = "System Power: OFF"
                self.isOn = False
        else:
            self.messagetext = "System Power: ON"
            self.isOn = True
            
            ##TODO: This might need to not go here?????
            self.isStopped = False
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def emergencyStop(self, addr):
        self.messagetext = "System Power: OFF"
        self.isOn = False
        self.isStopped = True
        self.plc.emergencyStop()
        self.commandSock.sendto(self.messagetext.encode(), addr)


    def openDoors(self,addr):
        if self.isOn and not self.isStopped:
            self.messagetext = "Doors: OPEN"
            self.isDoorOpen = True
            self.plc.openDoors()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        self.commandSock.sendto(self.messagetext.encode(), addr)
        print(self.messagetext + " " + str(self.addr[0]))


    def closeDoors(self, addr):
        if not self.isStopped and not self.isPadExtended and self.isOn:
            self.messagetext = "Doors: CLOSED"
            self.isDoorOpen = False
            self.plc.closeDoors()
        else:
            self.messagetext = ERROR_PREFIX
            if self.isStopped:
                self.messagetext = self.messagetext + errorDictionary['isStopped'] + '. '
            if self.isPadExtended:
                self.messagetext = self.messagetext + errorDictionary['padIsExtended'] + '. '

        self.commandSock.sendto(self.messagetext.encode(), addr)

    def openRoof(self, addr):
        if self.isOn:
            self.messagetext = "Roof: OPEN"
            self.isRoofOpen = True
            self.plc.openRoof()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def closeRoof(self, addr):
        if not self.isStopped and not self.isPadRaised and self.isOn:
            self.messagetext = "Roof: CLOSED"
            self.isRoofOpen = False
            self.plc.closeRoof()
        else:
            self.messagetext = ERROR_PREFIX
            if self.isStopped:
                self.messagetext = self.messagetext + errorDictionary['isStopped'] + '. '
            if self.isPadRaised:
                self.messagetext = self.messagetext + errorDictionary['padIsRaised'] + '. '

        self.commandSock.sendto(self.messagetext.encode(), addr)

    def extendPad(self, addr):
        if self.isOn and self.isDoorOpen and not self.isStopped:
            self.messagetext = "Back Pad: EXTENDED"
            self.isPadExtended = True
            self.plc.extendPad()
        else:
            self.messagetext = ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + errorDictionary['isOff'] + '. '
            if not self.isDoorOpen:
                self.messagetext = self.messagetext + errorDictionary['doorsAreClosed'] + '. '

        self.commandSock.sendto(self.messagetext.encode(), addr)

    def retractPad(self, addr):
        if not self.isStopped and self.isOn:
            self.messagetext = "Back Pad: RETRACTED"
            self.isPadExtended = False
            self.plc.retractPad()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isStopped']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def raisePad(self, addr):
        if self.isOn and self.isRoofOpen and not self.isStopped:
            self.messagetext = "Top Pad: RAISED"
            self.isPadRaised = True
            self.plc.raisePad()
        else:
            self.messagetext = ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + errorDictionary['isOff'] + '. '
            if not self.isRoofOpen:
                self.messagetext = self.messagetext + errorDictionary['roofIsClosed'] + '. '
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def lowerPad(self, addr):
        if not self.isStopped:
            self.messagetext = "Top Pad: LOWERED"
            self.isPadRaised = False
            self.plc.lowerPad()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isStopped']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def sendTestMessage(self, addr):
        self.messagetext = "Connection is good. Message recieved" 
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def handledata(self, data, addr):
        print(data)
        
        if data == "systemPower":
            self.systemPower(addr)
        elif data == "emergencyStop":
            self.emergencyStop(addr)
        elif data == "openDoors":
            self.openDoors(addr)
        elif data == "closeDoors":
            self.closeDoors(addr)
        elif data == "openRoof":
            self.openRoof(addr)
        elif data == "closeRoof":
            self.closeRoof(addr)
        elif data == "extendPad":
            self.extendPad(addr)
        elif data == "retractPad":
            self.retractPad(addr)
        elif data == "raisePad":
            self.raisePad(addr)
        elif data == "lowerPad":
            self.lowerPad(addr)
        elif data == "systemStatus":
            self.systemStatus(addr)
        elif "Connection Test" in data:
            self.sendTestMessage(addr)
        else:
            self.unknownMessage(addr)

        self.serverCallback()


    def receivedata(self):
        while self.running:
            data = None
            while data is None:
                try: 
                    data, addr = self.commandSock.recvfrom(1024)
                except Exception as e:
                    print("Server.receiveData exception:" + str(e))
                    self.closeSockets()
                    return
                
            data = data.decode()
            print((data,addr))
            self.handledata(data, addr)
        self.closeSockets()


    def connection(self):
        try:
            self.commandSock.bind((UDP_IP_ADDRESS, UDP_CLIENT_PORT_NUM))
            self.isConnected = True
            data, self.addr = self.commandSock.recvfrom(1024)
            data = data.decode()

        except OSError as e:
            print("Server.connection OSError: " + str(e))
            
        self.commandthread = threading.Thread(target=self.receivedata)
        self.commandthread.start()