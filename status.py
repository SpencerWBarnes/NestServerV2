'''Author: Claudia N. 
    TCP server built to run on a seperate thread'''

import time
import threading
import json
from PlcClient import PlcClient, PlcClientDev #TODO: remove dev
import StringConstants as strings
from pad_plot import Pad_Plot
import random


######### Important constants #########
# default values for IP and Port (IPV4 on Windows, en0 on OSX)
IP_ADDRESS = '192.168.0.6'
# IP_ADDRESS = '192.168.99.2' # THE NEST's IP

PORT_NUM = 8888
BUFFERSIZE = 1024


######### Server Class #########
# This is a guiless server. It runs in the background in pyfladesklocal.py
class MachineStatus():
    def __init__(self, parent=None):
        
        # States
        self.running = True
        self.isOn = False
        self.isDoorOpen = False
        self.isRoofOpen = False
        self.isPadExtended = False
        self.isPadRaised = False

        # TODO: maybe get drone radius from drone? maybe from server?
        self.bottomPadPlot = Pad_Plot(16, name='Bottom')
        self.topPadPlot = Pad_Plot(16, name='Top')

        self.messagetext = ""

        # PlcClient
        # self.plc = PlcClient()          # This is for production mode
        self.plc = PlcClientDev()       # This is for development mode. It makes a client with empty functions
        # self.plc.login("PLC")           # Login with password PLC
        self.plc.initButtons()          # Gets button information from the PlcClient browser window

    # systemStatus: Sends a JSON string to the client to show the state of the NEST
    def systemStatus(self):
        systemStatusDict = {
            "isOn" : self.isOn,
            "isDoorOpen" : self.isDoorOpen,
            "isRoofOpen" : self.isRoofOpen,
            "isPadExtended" : self.isPadExtended,
            "isPadRaised" : self.isPadRaised,
            "previousCommand" : self.messagetext
        }
        message = json.dumps(systemStatusDict)
        return message
    
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
    def systemPower(self):
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
        return self.messagetext

    # emergencyStop:    Called when the client wants to stop all mototrs on the nest,
    #                   used for setting the isOn variable to false
    def emergencyStop(self):
        self.messagetext = "System Power: OFF"
        self.isOn = False
        self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_EMERGENCY_STOP))
        return self.messagetext

    # openDoors:    Called when the client wants to open the nest doors,
    #               used for setting the isDoorOpen variable to true
    def openDoors(self):
        if self.isOn:
            self.messagetext = "Doors: OPEN"
            self.isDoorOpen = True
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_OPEN_DOORS))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        return self.messagetext

    # closeDoors:   Called when the client wants to close the nest doors,
    #               used for setting the isDoorOpen variable to false
    def closeDoors(self):
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

        return self.messagetext

    # openRoof:     Called when the client wants to open the nest roof,
    #               used for setting the isRoofOpen variable to true
    def openRoof(self):
        if self.isOn:
            self.messagetext = "Roof: OPEN"
            self.isRoofOpen = True
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_OPEN_ROOF))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        return self.messagetext

    # openRoof:     Called when the client wants to close the nest roof,
    #               used for setting the isRoofOpen variable to false
    def closeRoof(self):
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

        return self.messagetext

    # extendPad:    Called when the client wants to extend the nest landing pad,
    #               used for setting the isPadExtended variable to true
    def extendPad(self):
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

                
        return self.messagetext

    # retractPad:   Called when the client wants to retract the nest landing pad,
    #               used for setting the isPadExtended variable to false
    def retractPad(self):
        if self.isOn:
            self.messagetext = "Back Pad: RETRACTED"
            self.isPadExtended = False
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_RETRACT_PAD))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        return self.messagetext

    # raisePad:     Called when the client wants to raise the nest landing pad,
    #               used for setting the isPadRaised variable to true
    def raisePad(self):
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
        

        return self.messagetext

    # lowerPad:     Called when the client wants to lower the nest landing pad,
    #               used for setting the isPadRaised variable to false
    def lowerPad(self):
        if self.isOn:
            self.messagetext = "Top Pad: LOWERED"
            self.isPadRaised = False
            self.startThread(lambda: self.plc.executeCommand(strings.MESSAGE_LOWER_PAD))
        else:
            self.messagetext = strings.ERROR_PREFIX + strings.ERROR_IS_OFF

        return self.messagetext
    
    def bottomDroneMission(self):
        if self.isOn:
            self.messagetext = "Bottom drone mission"
        
            self.isDoorOpen = True
            self.plc.executeCommand(strings.MESSAGE_OPEN_DOORS)
        
            self.isPadExtended = True
            self.plc.executeCommand(strings.MESSAGE_EXTEND_PAD)

            # time.sleep(10) # TODO: SEND DRONE OUT

            # Drone landing
            x = 1000
            y = 1000
            h = random.random() * 360
            
            while self.bottomPadPlot.is_safe(x, y) is 'r':
                print ("Drone is not safe: x = " + str(x) + " y = " + str(y))
                time.sleep(2) # TODO: SEND DRONE OUT
                x = random.random() * self.bottomPadPlot.pad_radius
                y = random.random() * self.bottomPadPlot.pad_radius
                h = random.random() * 360
                self.bottomPadPlot.plot_drone(x, y, h)
            
            print ("Drone is safe: x = " + str(x) + " y = " + str(y) + " Proceed to retract pad")

            self.isPadExtended = False
            self.plc.executeCommand(strings.MESSAGE_RETRACT_PAD)
            
            self.isDoorOpen = False
            self.plc.executeCommand(strings.MESSAGE_CLOSE_DOORS)
            
        else:
            self.messagetext = "TODO: error message"
        
            return self.messagetext

    def topDroneMission(self):
        if self.isOn:
            self.messagetext = "Top drone mission"
            
            self.isRoofOpen = True
            self.plc.executeCommand(strings.MESSAGE_OPEN_ROOF)
        
            self.isPadRaised = True
            self.plc.executeCommand(strings.MESSAGE_RAISE_PAD)

            # Drone landing
            x = 1000
            y = 1000
            h = random.random() * 360
            
            while self.topPadPlot.is_safe(x, y) is 'r':
                print ("Drone is not safe: x = " + str(x) + " y = " + str(y))
                time.sleep(2) # TODO: SEND DRONE OUT
                x = random.random() * self.topPadPlot.pad_radius
                y = random.random() * self.topPadPlot.pad_radius
                h = random.random() * 360
                self.topPadPlot.plot_drone(x, y, h)
            
            print ("Drone is safe: x = " + str(x) + " y = " + str(y) + " Proceed to lower pad")

            self.isPadRaised = False
            self.plc.executeCommand(strings.MESSAGE_LOWER_PAD)
            
            self.isRoofOpen = False
            self.plc.executeCommand(strings.MESSAGE_CLOSE_ROOF)
        else:
            self.messagetext = "TODO: error message"
        
        return self.messagetext

    def startThread(self, threadTarget):
        thread = threading.Thread(target=threadTarget)
        thread.daemon = True
        thread.start()
        return thread