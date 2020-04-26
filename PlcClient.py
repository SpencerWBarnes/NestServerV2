from selenium import webdriver
import time
import threading
import StringConstants as strings

TIMEDELAY = 3

# These come from the ID's of elements in the HTML
OPEN_DOORS_ID       = "157910241216714"
CLOSE_DOORS_ID      = "157910667129821"
EMERGENCY_STOP_ID   = "157910667599022"
EXTEND_PAD_ID       = "157910679857925"
RETRACT_PAD_ID      = "157910680336426"
CLOSE_ROOF_ID       = "157910681743328"
RAISE_PAD_ID        = "157910682081829"
LOWER_PAD_ID        = "157910682381830"
OPEN_ROOF_ID        = "157910689748631"
DOOR_ONE_CLOSED_ID  = "158092495274536"
DOOR_TWO_CLOSED_ID  = "158092496252337"
RAIL_RETRACTED_ID   = "158092497361138"
ROOF_CLOSED_ID      = "158092497820339"
LIFT_LOWERED_ID     = "158092498570540"
RAIL_EXTENDED_ID    = "158092500511041"
ROOF_OPEN_ID        = "158092500512742"
DOOR_TWO_OPEN_ID    = "158092500514543"
DOOR_ONE_OPEN_ID    = "158092500516544"
LIFT_RAISED_ID      = "158092500518645"

# TODO: Possible problem, the plc client and the server can actually exist in different states if the server is too quick to send command.
#       When the plc receives a message that it can't handle or process right now because of constraints, it ignores that message. 
#       This means that the plc will ignore messages like "__extendPad" while it is in the process of opening the doors. 
#       So what should we do? I'm thinking we send back response messages on whether or not a task can be completed. 
#       Or we could share some sort of global status between the server and the plc client

class Sensor:
    def __init__(self, id, browser):
        self.button = browser.find_element_by_id(id)
        # TODO in Nest: see if this is needed
        # self.button = div.find_element_by_tag_name("P")
        self.getModeValue()

    # toggleButton: This clicks a button twice with a time delay in between
    def getModeValue(self):
        if (self.button.get_attribute("innerHTML") == "ON"):
            return True
        else:
            return False

class Button:
    def __init__(self, id, browser, waitSensors):
        self.button = browser.find_element_by_id(id)
        self.waitSensors = waitSensors
        self.shouldBeOn = False

    # toggleButton: This clicks a button twice with a time delay in between
    def toggleButton(self):
        self.button.click()
        self.shouldBeOn = True
        
        sensorsTriggered = False
        while(not sensorsTriggered):
            if (not self.shouldBeOn):
                break
            
            sensorsTriggered = True
            for sensor in self.waitSensors:
                if (not sensor.getModeValue()):
                    sensorsTriggered = False
                    
        self.shouldBeOn = False
        self.button.click()

class PlcClient:
    # init sets up the browser
    def __init__(self):
        self.browser = webdriver.Chrome(strings.CHROMEDRIVERLOCATION)

        # TODO: remove
        self.browser.get('http://localhost:3000/')

    # login: navigates to the login url and enters in password. This opens our custom webpage for the PLC
    def login(self, password):
        self.browser.get(strings.PLCURL)
        time.sleep(TIMEDELAY)
        passwordField = self.browser.find_element_by_id("input_password")
        passwordField.send_keys(password)
        checkbox = self.browser.find_element_by_id("check_logoncustomized")
        checkbox.click()
        login = self.browser.find_element_by_id("button_login")
        login.click()
        time.sleep(TIMEDELAY)

    # initButtons: finds all the buttons in the HTML from the browser using the Button class
    def initButtons(self):
        self.doorOneClosedText = Sensor(DOOR_ONE_CLOSED_ID, self.browser)
        self.doorTwoClosedText = Sensor(DOOR_TWO_CLOSED_ID, self.browser)
        self.railRetractedText = Sensor(RAIL_RETRACTED_ID, self.browser)
        self.roofClosedText = Sensor(ROOF_CLOSED_ID, self.browser)
        self.liftLoweredText = Sensor(LIFT_LOWERED_ID, self.browser)
        self.railExtendedText = Sensor(RAIL_EXTENDED_ID, self.browser)
        self.roofOpenText = Sensor(ROOF_OPEN_ID, self.browser)
        self.doorTwoOpenText = Sensor(DOOR_TWO_OPEN_ID, self.browser)
        self.doorOneOpenText = Sensor(DOOR_ONE_OPEN_ID, self.browser)
        self.liftRaisedText = Sensor(LIFT_RAISED_ID, self.browser)

        self.openDoorsButton = Button(OPEN_DOORS_ID, self.browser, [self.doorTwoOpenText, self.doorOneOpenText])
        self.closeDoorsButton = Button(CLOSE_DOORS_ID, self.browser, [self.doorOneClosedText, self.doorTwoClosedText])
        self.emergencyStopButton = Button(EMERGENCY_STOP_ID, self.browser, [])
        self.extendPadButton = Button(EXTEND_PAD_ID, self.browser, [self.railExtendedText])
        self.retractPadButton = Button(RETRACT_PAD_ID, self.browser, [self.railRetractedText])
        self.closeRoofButton = Button(CLOSE_ROOF_ID, self.browser, [self.roofClosedText])
        self.raisePadButton = Button(RAISE_PAD_ID, self.browser, [self.liftRaisedText])
        self.lowerPadButton = Button(LOWER_PAD_ID, self.browser, [self.liftLoweredText])
        self.openRoofButton = Button(OPEN_ROOF_ID, self.browser, [self.roofOpenText])

    # executeCommand: takes in a string command, the same one the server sees, and executes it
    def executeCommand(self, command):
        canExecute = True

        if command == strings.MESSAGE_EMERGENCY_STOP:
            self.__emergencyStop()

        elif command == strings.MESSAGE_OPEN_DOORS:
            self.__openDoors()

        elif command == strings.MESSAGE_CLOSE_DOORS:
            if(self.railRetractedText.getModeValue()):
                self.__closeDoors()
            else: 
                canExecute = False

        elif command == strings.MESSAGE_OPEN_ROOF:
            self.__openRoof()

        elif command == strings.MESSAGE_CLOSE_ROOF:
            if(self.liftLoweredText.getModeValue()):
                self.__closeRoof()
            else: 
                canExecute = False

        elif command == strings.MESSAGE_EXTEND_PAD:
            if(self.doorOneOpenText.getModeValue() and self.doorTwoOpenText.getModeValue()):
                self.__extendPad()
            else: 
                canExecute = False

        elif command == strings.MESSAGE_RETRACT_PAD:
            self.__retractPad()

        elif command == strings.MESSAGE_RAISE_PAD:
            if(self.roofOpenText.getModeValue()):
                self.__raisePad()
            else: 
                canExecute = False

        elif command == strings.MESSAGE_LOWER_PAD:
            self.__lowerPad()

        elif command == strings.MESSAGE_SYSTEM_STATUS:
            self.__systemStatus()

        return (canExecute)

    # close: needs to be called no matter what to close the browser
    def close(self):
        try:
            self.browser.close()
        except Exception as e: # it might through an exception if the browser has already been closed
            print("PlcClient.close exception:" + str(e))

    # Individual operations: These functions handle each of the buttons actions on the screen, 
    #   these are private methods to prevent outside objects from using them improperly
    def __emergencyStop(self):
        # TODO: see if this already happens in the PLC
        self.openDoorsButton.shouldBeOn = False
        self.closeDoorsButton.shouldBeOn = False
        self.extendPadButton.shouldBeOn = False
        self.retractPadButton.shouldBeOn = False
        self.closeRoofButton.shouldBeOn = False
        self.raisePadButton.shouldBeOn = False
        self.lowerPadButton.shouldBeOn = False
        self.openRoofButton.shouldBeOn = False
        self.emergencyStopButton.toggleButton()

    def __openDoors(self):
        # TODO: Check sensors
        self.closeDoorsButton.shouldBeOn = False
        self.openDoorsButton.toggleButton()

    def __closeDoors(self):
        self.openDoorsButton.shouldBeOn = False
        self.closeDoorsButton.toggleButton()

    def __openRoof(self):
        # TODO: Check sensors
        self.closeRoofButton.shouldBeOn = False
        self.openRoofButton.toggleButton()
        return True

    def __closeRoof(self):
        self.openRoofButton.shouldBeOn = False
        self.closeRoofButton.toggleButton() 

    def __extendPad(self):
        self.retractPadButton.shouldBeOn = False
        self.extendPadButton.toggleButton()

    def __retractPad(self):
        # TODO: Check sensors
        self.extendPadButton.shouldBeOn = False
        self.retractPadButton.toggleButton()
        return True

    def __raisePad(self):
        self.lowerPadButton.shouldBeOn = False
        self.raisePadButton.toggleButton()

    def __lowerPad(self):
        # TODO: Check sensors
        self.raisePadButton.shouldBeOn = False
        self.lowerPadButton.toggleButton()
        return True

    def areDoorsOpen(self):
        doorTwoOpen = self.doorTwoOpenText.getModeValue() 
        doorOneOpen = self.doorOneOpenText.getModeValue() 
        return (doorTwoOpen and doorOneOpen)

    def areDoorsClosed(self):
        doorOneClosed = self.doorOneClosedText.getModeValue() 
        doorTwoClosed = self.doorTwoClosedText.getModeValue() 
        return (doorOneClosed and doorTwoClosed)

    def isRoofOpen(self):
        return self.roofOpenText.getModeValue() 

    def isRoofClosed(self):
        return self.roofClosedText.getModeValue() 

    def isRailExtended(self):
        return self.railExtendedText.getModeValue() 

    def isRailRetracted(self):
        return self.railRetractedText.getModeValue() 

    def isLiftRaised(self):
        return self.liftRaisedText.getModeValue() 

    def isLiftLowered(self):
        return self.liftLoweredText.getModeValue() 

# This is a fake plc client so that we don't have to be connected to the plc to do normal developing
# It has all of the same public functions as PlcClient, but they are empty. This helps us not have to open a 
# browser to the PLC's site everytime we want to test something on the server.
class PlcClientDev:
    def __init__(self):
        pass

    def login(self, password):
        pass

    def initButtons(self):
        pass

    def executeCommand(self, command):
        pass

    def areDoorsOpen(self):
        pass

    def areDoorsClosed(self):
        pass

    def isRoofOpen(self):
        pass

    def isRoofClosed(self):
        pass

    def isRailExtended(self):
        pass

    def isRailRetracted(self):
        pass

    def isLiftRaised(self):
        pass

    def isLiftLowered(self):
        pass

    def close(self):
        pass