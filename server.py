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

UDP_CLIENT_PORT_NUM = 8888

BUFFERSIZE = 1024

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
        self.openConnections = []

        # messagetext: holds the value of the message to be sent to the client
        self.messagetext = None

        # PlcClient
        # self.plc = PlcClient()          # This is for production mode
        self.plc = PlcClientDev()       # This is for development mode. It makes a client with empty functions
        # self.plc.login("PLC")           # Login with password PLC
        self.plc.initButtons()          # Gets button information from the PlcClient browser window
        
        # sockets
        self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        #Port: 8000


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

    def closeConnections(self):
        for conn in self.openConnections:
            conn.close()

    # closeEvent:   When the gui is closed, close the plc browser and all the sockets     
    def closeEvent(self):
        self.plc.close()
        self.closeSockets()


    ######### Server Message Handling #########

    # unknownMessage: This method is called when the server receives a message it doesn't know what to do with it
    def unknownMessage(self, conn):
        self.messagetext = ERROR_PREFIX + errorDictionary['unknownMessage']
        conn.send(self.messagetext.encode())

    # systemStatus: Sends a JSON string to the client to show the state of the NEST
    def systemStatus(self, conn):
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
        conn.send(message.encode())

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
    def systemPower(self, conn):
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

        conn.send(self.messagetext.encode())

    # emergencyStop:    Called when the client wants to stop all mototrs on the nest,
    #                   used for setting the isOn variable to false
    def emergencyStop(self, conn):
        self.messagetext = "System Power: OFF"
        self.isOn = False
        self.plc.emergencyStop()
        conn.send(self.messagetext.encode())

    # openDoors:    Called when the client wants to open the nest doors,
    #               used for setting the isDoorOpen variable to true
    def openDoors(self,conn):
        if self.isOn:
            self.messagetext = "Doors: OPEN"
            self.isDoorOpen = True
            self.plc.openDoors()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        conn.send(self.messagetext.encode())

    # closeDoors:   Called when the client wants to close the nest doors,
    #               used for setting the isDoorOpen variable to false
    def closeDoors(self, conn):
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

        conn.send(self.messagetext.encode())

    # openRoof:     Called when the client wants to open the nest roof,
    #               used for setting the isRoofOpen variable to true
    def openRoof(self, conn):
        if self.isOn:
            self.messagetext = "Roof: OPEN"
            self.isRoofOpen = True
            self.plc.openRoof()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        conn.send(self.messagetext.encode())

    # openRoof:     Called when the client wants to close the nest roof,
    #               used for setting the isRoofOpen variable to false
    def closeRoof(self, conn):
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

        conn.send(self.messagetext.encode())

    # extendPad:    Called when the client wants to extend the nest landing pad,
    #               used for setting the isPadExtended variable to true
    def extendPad(self, conn):
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

        conn.send(self.messagetext.encode())

    # retractPad:   Called when the client wants to retract the nest landing pad,
    #               used for setting the isPadExtended variable to false
    def retractPad(self, conn):
        if self.isOn:
            self.messagetext = "Back Pad: RETRACTED"
            self.isPadExtended = False
            self.plc.retractPad()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        conn.send(self.messagetext.encode())

    # raisePad:     Called when the client wants to raise the nest landing pad,
    #               used for setting the isPadRaised variable to true
    def raisePad(self, conn):
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
        conn.send(self.messagetext.encode())

    # lowerPad:     Called when the client wants to lower the nest landing pad,
    #               used for setting the isPadRaised variable to false
    def lowerPad(self, conn):
        if self.isOn:
            self.messagetext = "Top Pad: LOWERED"
            self.isPadRaised = False
            self.plc.lowerPad()
        else:
            self.messagetext = ERROR_PREFIX + errorDictionary['isOff']
        conn.send(self.messagetext.encode())

    # sendTestMessage:  Used to send a client a message to test the connection
    def sendTestMessage(self, conn):
        self.messagetext = "Connection is good. Message recieved" 
        conn.send(self.messagetext.encode())

    # handledata:   This is used to decipher the messages sent by the client
    def handledata(self, data, conn):
        print(data)
        
        if data == "systemPower":
            self.systemPower(conn)
        elif data == "emergencyStop":
            self.emergencyStop(conn)
        elif data == "openDoors":
            self.openDoors(conn)
        elif data == "closeDoors":
            self.closeDoors(conn)
        elif data == "openRoof":
            self.openRoof(conn)
        elif data == "closeRoof":
            self.closeRoof(conn)
        elif data == "extendPad":
            self.extendPad(conn)
        elif data == "retractPad":
            self.retractPad(conn)
        elif data == "raisePad":
            self.raisePad(conn)
        elif data == "lowerPad":
            self.lowerPad(conn)
        elif data == "systemStatus":
            self.systemStatus(conn)
        elif "Connection Test" in data:
            self.sendTestMessage(conn)
        else:
            self.unknownMessage(conn)

        self.serverCallback()

    def startClientThread(self, conn):
        serverThread = threading.Thread(target=self.receivedata, args=[conn])
        serverThread.daemon = True
        serverThread.start()

    # Server function for receiving data. It passes the received data to handleData
    def receivedata(self, conn):
        print("test")
        while True:
            data = conn.recv(BUFFERSIZE)
            if data: 
                print ("received data:", data.decode())
                self.handledata(data.decode(), conn)
            data = None
        conn.close()

    # Server function for setting up the connection. It starts receiveData on a seperate thread
    def connection(self):
        try:
            self.commandSock.bind((UDP_IP_ADDRESS, UDP_CLIENT_PORT_NUM))
            self.commandSock.listen(10)

        except OSError as e:
                print("Server.connection OSError: " + str(e))
        
        while True: 
            conn, addr = self.commandSock.accept()
            self.openConnections.append(conn)
            # data = conn.recv(BUFFERSIZE)
            # message = "Message revieved! " + data.decode()
            # conn.send(message.encode())
            self.startClientThread(conn)
            print ('Connection address:', addr)