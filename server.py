'''Author: Lily S. and Claudia N. 
    Simple UDP server built to run on a seperate thread'''

import socket
import sys
import time
import threading
import json
from PlcClient import PlcClient, PlcClientDev #TODO: remove dev

######### Important constants #########
# default values for IP and Port (IPV4 on Windows, en0 on OSX)
UDP_IP_ADDRESS = '192.168.0.8'
# UDP_IP_ADDRESS = '192.168.99.2' # THE NEST's IP

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
            "isStarted" : "Must stop system"
        }


######### Server Class #########
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
        self.isConnected = False

        # messagetext: holds the value of the message to be sent to the client
        self.messagetext = None

        # PlcClient
        self.plc = PlcClient()          # This is for production mode
        # self.plc = PlcClientDev()       # This is for development mode. It makes a client with empty functions
        # self.plc.login("PLC")           # Login with password PLC
        self.plc.initButtons()          # Gets button information from the PlcClient browser window

        # connectThread: setting the daemon attribute to True makes it so that when the main thread is exited, so is this thread
        self.connectThread = threading.Thread(target=self.connection)
        self.connectThread.daemon = True
        
        # sockets
        self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        #Port: 8000


    ######### Server Setup Functions #########

    # serverCallback: A function that should be overridden in pyfladesklocal.py in order to update the server's UI
    def serverCallback(self):
        print("serverCallback: you should override this")

    # closeSocket:  Run when the server is taken down to ensure that the socket is closed. 
    #               This usually throws the exception, but I have this function called just in case.
    def closeSocket(self, mSocket):
        try:
            mSocket.shutdown(socket.SHUT_RDWR)
            mSocket.close()
        except Exception as e: # This is usually thrown, but that's okay. 
            print("Server.closeSocket exception: " + str(e))

    # closeSockets: This function closes all sockets in the program. We used to have more, but now all we have is commandSock
    def closeSockets(self):
        self.running = False
        self.closeSocket(self.commandSock)

    # closeEvent:   When the gui is closed, close the plc browser and all the sockets     
    def closeEvent(self):
        self.plc.close()
        self.closeSockets()


    ######### Server Message Handling #########

    # unknownMessage: This method is called when the server receives a message it doesn't know what to do with it
    def unknownMessage(self, addr):
        self.messagetext = ERROR_PREFIX + errorDictionary['unknownMessage']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    # systemStatus: Sends a JSON string to the client to show the state of the NEST
    def systemStatus(self, addr):
        systemStatusDict = {
            "isOn" : self.isOn,
            "isDoorOpen" : self.isDoorOpen,
            "isRoofOpen" : self.isRoofOpen,
            "isPadExtended" : self.isPadExtended,
            "isPadRaised" : self.isPadRaised,
            "previousCommand" : self.messagetext
        }
        message = json.dumps(systemStatusDict)
        # print(message)
        self.commandSock.sendto(message.encode(), addr)

    # getSystemStatusDict: like systemStatus, but returns a dictionary of the state of the NEST - doesn't send messages to the client
    def getSystemStatusDict(self):
        systemStatusDict = {
            "isOn" : self.isOn,
            "isDoorOpen" : self.isDoorOpen,
            "isRoofOpen" : self.isRoofOpen,
            "isPadExtended" : self.isPadExtended,
            "isPadRaised" : self.isPadRaised,
            "previousCommand" : self.messagetext
        }
        return systemStatusDict

    # systemPower:  Called when the client wants to start sending messages that affect the state of the NEST,
    #               used for setting the isOn variable to true
    def systemPower(self, addr):
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

        self.commandSock.sendto(self.messagetext.encode(), addr)

    # emergencyStop:    Called when the client wants to stop all mototrs on the nest,
    #                   used for setting the isOn variable to false
    def emergencyStop(self, addr):
        self.messagetext = "System Power: OFF"
        self.isOn = False
        self.plc.emergencyStop()
        self.commandSock.sendto(self.messagetext.encode(), addr)

    # openDoors:    Called when the client wants to open the nest doors,
    #               used for setting the isDoorOpen variable to true
    def openDoors(self,addr):
        if self.isOn:
            self.messagetext = "Doors: OPEN"
            self.isDoorOpen = True
            self.plc.openDoors()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        self.commandSock.sendto(self.messagetext.encode(), addr)
        print(self.messagetext + " " + str(self.addr[0]))

    # closeDoors:   Called when the client wants to close the nest doors,
    #               used for setting the isDoorOpen variable to false
    def closeDoors(self, addr):
        if not self.isPadExtended and self.isOn:
            self.messagetext = "Doors: CLOSED"
            self.isDoorOpen = False
            self.plc.closeDoors()
        else:
            self.messagetext = ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + errorDictionary['isOff'] + '. '
            if self.isPadExtended:
                self.messagetext = self.messagetext + errorDictionary['padIsExtended'] + '. '

        self.commandSock.sendto(self.messagetext.encode(), addr)

    # openRoof:     Called when the client wants to open the nest roof,
    #               used for setting the isRoofOpen variable to true
    def openRoof(self, addr):
        if self.isOn:
            self.messagetext = "Roof: OPEN"
            self.isRoofOpen = True
            self.plc.openRoof()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    # openRoof:     Called when the client wants to close the nest roof,
    #               used for setting the isRoofOpen variable to false
    def closeRoof(self, addr):
        if not self.isPadRaised and self.isOn:
            self.messagetext = "Roof: CLOSED"
            self.isRoofOpen = False
            self.plc.closeRoof()
        else:
            self.messagetext = ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + errorDictionary['isOff'] + '. '
            if self.isPadRaised:
                self.messagetext = self.messagetext + errorDictionary['padIsRaised'] + '. '

        self.commandSock.sendto(self.messagetext.encode(), addr)

    # extendPad:    Called when the client wants to extend the nest landing pad,
    #               used for setting the isPadExtended variable to true
    def extendPad(self, addr):
        if self.isOn and self.isDoorOpen:
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

    # retractPad:   Called when the client wants to retract the nest landing pad,
    #               used for setting the isPadExtended variable to false
    def retractPad(self, addr):
        if self.isOn:
            self.messagetext = "Back Pad: RETRACTED"
            self.isPadExtended = False
            self.plc.retractPad()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    # raisePad:     Called when the client wants to raise the nest landing pad,
    #               used for setting the isPadRaised variable to true
    def raisePad(self, addr):
        if self.isOn and self.isRoofOpen:
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

    # lowerPad:     Called when the client wants to lower the nest landing pad,
    #               used for setting the isPadRaised variable to false
    def lowerPad(self, addr):
        if self.isOn:
            self.messagetext = "Top Pad: LOWERED"
            self.isPadRaised = False
            self.plc.lowerPad()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        self.commandSock.sendto(self.messagetext.encode(), addr)

    def bottomDroneMission(self, addr):
        if self.isOn:
            self.messagetext = "Bottom drone mission"
            self.isDoorOpen = True
            self.isPadExtended = True
            # self.plc.bottomDroneMission()
        else:
            self.messagetext = "TODO: error message"
        self.commandSock.sendto(self.messagetext.encode(), addr)
        print(self.messagetext + " " + str(self.addr[0]))

    def topDroneMission(self, addr):
        if self.isOn:
            self.messagetext = "Top drone mission"
            self.isRoofOpen = True
            self.isPadRaised = True
            # self.plc.topDroneMission()
        else:
            self.messagetext = "TODO: error message"
        self.commandSock.sendto(self.messagetext.encode(), addr)
        print(self.messagetext + " " + str(self.addr[0]))

    # sendTestMessage:  Used to send a client a message to test the connection
    def sendTestMessage(self, addr):
        self.messagetext = "Connection is good. Message recieved" 
        self.commandSock.sendto(self.messagetext.encode(), addr)

    # handledata:   This is used to decipher the messages sent by the client
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
        elif data == "bottomDroneMission":
            self.bottomDroneMission(addr)
        elif data == "topDroneMission":
            self.topDroneMission(addr)
        elif "Connection Test" in data:
            self.sendTestMessage(addr)
        else:
            self.unknownMessage(addr)

        self.serverCallback()

    # Server function for receiving data. It passes the received data to handleData
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

    # Server function for setting up the connection. It starts receiveData on a seperate thread
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