'''Author: Claudia N. 
    TCP server built to run on a seperate thread'''

import socket
import sys
import time
import threading
import json
from PlcClient import PlcClient, PlcClientDev #TODO: remove dev
import StringConstants as strings

######### Important constants #########
# default values for IP and Port (IPV4 on Windows, en0 on OSX)
IP_ADDRESS = '192.168.0.11'
# IP_ADDRESS = '192.168.99.2' # THE NEST's IP

PORT_NUM = 8888
BUFFERSIZE = 1024


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
        self.plc = PlcClient()          # This is for production mode
        # self.plc = PlcClientDev()       # This is for development mode. It makes a client with empty functions
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
    def closeSocket(self):
        try:
            self.commandSock.shutdown(socket.SHUT_RDWR)
            self.commandSock.close()
        except Exception as e: # This is usually thrown, but that's okay. 
            print("Server.closeSocket exception: " + str(e))

    # closeConnections: This function closes all open connections to clients
    def closeConnections(self):
        for conn in self.openConnections:
            conn.close()

    # closeEvent:   When the gui is closed, close the plc browser and all the sockets     
    def closeEvent(self):
        self.plc.close()
        self.closeSocket()


    ######### Server Message Handling #########

    # unknownMessage: This method is called when the server receives a message it doesn't know what to do with it
    def unknownMessage(self, conn, message):
        self.messagetext = strings.ERROR_PREFIX + strings.ERROR_UNKNOWN_MESSAGE + ": " + message +'\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

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
        message = message + '\n'
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
                self.messagetext = strings.ERROR_PREFIX
                if self.isDoorOpen:
                    self.messagetext = self.messagetext + strings.ERROR_DOORS_ARE_OPEN
                if self.isRoofOpen:
                    self.messagetext = self.messagetext + strings.ERROR_ROOF_IS_OPEN
            else:
                self.messagetext = "System Power: OFF"
                self.isOn = False
        else:
            self.messagetext = "System Power: ON"
            self.isOn = True

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # emergencyStop:    Called when the client wants to stop all mototrs on the nest,
    #                   used for setting the isOn variable to false
    def emergencyStop(self, conn):
        self.messagetext = "System Power: OFF"
        self.isOn = False
        self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_EMERGENCY_STOP))
        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # openDoors:    Called when the client wants to open the nest doors,
    #               used for setting the isDoorOpen variable to true
    def openDoors(self,conn):
        if self.isOn:
            self.messagetext = "Doors: OPEN"
            self.isDoorOpen = True
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_OPEN_DOORS))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # closeDoors:   Called when the client wants to close the nest doors,
    #               used for setting the isDoorOpen variable to false
    def closeDoors(self, conn):
        if not self.isPadExtended and self.isOn:
            self.messagetext = "Doors: CLOSED"
            self.isDoorOpen = False
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_CLOSE_DOORS))
        else:
            self.messagetext = strings.ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + strings.ERROR_IS_OFF + '. '
            if self.isPadExtended:
                self.messagetext = self.messagetext + strings.ERROR_PAD_IS_EXTENDED + '. '

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # openRoof:     Called when the client wants to open the nest roof,
    #               used for setting the isRoofOpen variable to true
    def openRoof(self, conn):
        if self.isOn:
            self.messagetext = "Roof: OPEN"
            self.isRoofOpen = True
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_OPEN_ROOF))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # openRoof:     Called when the client wants to close the nest roof,
    #               used for setting the isRoofOpen variable to false
    def closeRoof(self, conn):
        if not self.isPadRaised and self.isOn:
            self.messagetext = "Roof: CLOSED"
            self.isRoofOpen = False
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_CLOSE_ROOF))
        else:
            self.messagetext = strings.ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + strings.ERROR_IS_OFF + '. '
            if self.isPadRaised:
                self.messagetext = self.messagetext + strings.ERROR_PAD_IS_RAISED + '. '

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # extendPad:    Called when the client wants to extend the nest landing pad,
    #               used for setting the isPadExtended variable to true
    def extendPad(self, conn):
        if self.isOn and self.isDoorOpen:
            self.messagetext = "Back Pad: EXTENDED"
            self.isPadExtended = True
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_EXTEND_PAD))
        else:
            self.messagetext = strings.ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + strings.ERROR_IS_OFF + '. '
            if not self.isDoorOpen:
                self.messagetext = self.messagetext + strings.ERROR_DOORS_ARE_CLOSED + '. '

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # retractPad:   Called when the client wants to retract the nest landing pad,
    #               used for setting the isPadExtended variable to false
    def retractPad(self, conn):
        if self.isOn:
            self.messagetext = "Back Pad: RETRACTED"
            self.isPadExtended = False
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_RETRACT_PAD))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # raisePad:     Called when the client wants to raise the nest landing pad,
    #               used for setting the isPadRaised variable to true
    def raisePad(self, conn):
        if self.isOn and self.isRoofOpen:
            self.messagetext = "Top Pad: RAISED"
            self.isPadRaised = True
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_RAISE_PAD))
        else:
            self.messagetext = strings.ERROR_PREFIX
            if not self.isOn:
                self.messagetext = self.messagetext + strings.ERROR_IS_OFF + '. '
            if not self.isRoofOpen:
                self.messagetext = self.messagetext + strings.ERROR_ROOF_IS_CLOSED + '. '
        
        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    # lowerPad:     Called when the client wants to lower the nest landing pad,
    #               used for setting the isPadRaised variable to false
    def lowerPad(self, conn):
        if self.isOn:
            self.messagetext = "Top Pad: LOWERED"
            self.isPadRaised = False
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_LOWER_PAD))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())
    
    def bottomDroneMission(self, conn):
        if self.isOn:
            self.messagetext = "Bottom drone mission"
            message = self.messagetext + '\n'
            conn.send(message.encode())
            
            # TODO: Get status of nest
            self.isDoorOpen = True
            self.plc.executeCommand(strings.MESSAGE_OPEN_DOORS)
        
            self.isPadExtended = True
            self.plc.executeCommand(strings.MESSAGE_EXTEND_PAD)

            self.isPadExtended = False
            self.plc.executeCommand(strings.MESSAGE_RETRACT_PAD)
            
            self.isDoorOpen = False
            self.plc.executeCommand(strings.MESSAGE_CLOSE_DOORS)
            
        else:
            self.messagetext = "TODO: error message"
        
            message = self.messagetext + '\n'
            conn.send(message.encode())

    def topDroneMission(self, conn):
        if self.isOn:
            self.messagetext = "Top drone mission"
            message = self.messagetext + '\n'
            conn.send(message.encode())
            
            self.isRoofOpen = True
            self.plc.executeCommand(strings.MESSAGE_OPEN_ROOF)
        
            self.isPadRaised = True
            self.plc.executeCommand(strings.MESSAGE_RAISE_PAD)

            self.isPadRaised = False
            self.plc.executeCommand(strings.MESSAGE_LOWER_PAD)
            
            self.isRoofOpen = False
            self.plc.executeCommand(strings.MESSAGE_CLOSE_ROOF)
        else:
            self.messagetext = "TODO: error message"
        
        message = self.messagetext + '\n'
        conn.send(message.encode())

    # sendTestMessage:  Used to send a client a message to test the connection
    def sendTestMessage(self, conn):
        self.messagetext = "Connection is good. Message recieved" 
        self.messagetext = self.messagetext + '\n'
        conn.send(self.messagetext.encode())
        print(self.messagetext.encode())

    def startThread(self, threadTarget):
        thread = threading.Thread(target=threadTarget)
        thread.daemon = True
        thread.start()
        return thread

    # handledata:   This is used to decipher the messages sent by the client
    def handledata(self, data, conn):
        if (data.endswith('\n')):
            data = data.replace('\n','')
        print(data)
        
        if data == strings.MESSAGE_SYSTEM_POWER:
            self.systemPower(conn)
        elif data == strings.MESSAGE_EMERGENCY_STOP:
            self.emergencyStop(conn)
        elif data == strings.MESSAGE_OPEN_DOORS:
            self.openDoors(conn)
        elif data == strings.MESSAGE_CLOSE_DOORS:
            self.closeDoors(conn)
        elif data == strings.MESSAGE_OPEN_ROOF:
            self.openRoof(conn)
        elif data == strings.MESSAGE_CLOSE_ROOF:
            self.closeRoof(conn)
        elif data == strings.MESSAGE_EXTEND_PAD:
            self.extendPad(conn)
        elif data == strings.MESSAGE_RETRACT_PAD:
            self.retractPad(conn)
        elif data == strings.MESSAGE_RAISE_PAD:
            self.raisePad(conn)
        elif data == strings.MESSAGE_LOWER_PAD:
            self.lowerPad(conn)
        elif data == strings.MESSAGE_SYSTEM_STATUS:
            self.systemStatus(conn)
        elif data == strings.MESSAGE_BOTTOM_DRONE_MISSION:
            self.startThread(lambda: self.bottomDroneMission(conn))
        elif data == strings.MESSAGE_TOP_DRONE_MISSION:
            self.startThread(lambda: self.topDroneMission(conn))
        elif strings.MESSAGE_CONNECTION_TEST in data:
            self.sendTestMessage(conn)
        else:
            self.unknownMessage(conn, data)

        self.serverCallback()

    # Setting up a thread for each client connected to receive data
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
                print ("received data:", data.decode(), conn)
                self.handledata(data.decode(), conn)
            data = None
        conn.close()

    # Server function for setting up the connection. It starts receiveData on a seperate thread
    def connection(self):
        try:
            self.commandSock.bind((IP_ADDRESS, PORT_NUM))
            self.commandSock.listen(10)

        except OSError as e:
            print("Server.connection OSError: " + str(e))
        
        while True: 
            conn, addr = self.commandSock.accept()
            self.openConnections.append(conn)
            self.startClientThread(conn)
            print ('Connection address:', addr)