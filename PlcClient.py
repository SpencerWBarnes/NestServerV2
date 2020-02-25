from selenium import webdriver
import time
import threading

# Location of chromedriver which can be downloaded from https://sites.google.com/a/chromium.org/chromedriver/ 
# download this and copy and paste where that file is here vvvv
# CHROMEDRIVERLOCATION = "C:\\Users\ECE436_18\Desktop\Scripts\chromedriver"
CHROMEDRIVERLOCATION = '/Users/claudia/Desktop/Impress/Server research/webscraper/chromedriver'
PLCURL = 'http://192.168.99.3/'
TIMEDELAY = 2

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

# TODO: Possible problem, the plc client and the server can actually exist in different states if the server is too quick to send data.
#       When the plc receives a message that it can't handle or process right now because of constraints, it ignores that message. 
#       This means that the plc will ignore messages like "extendPad" while it is in the process of opening the doors. 
#       So what should we do? I'm thinking we send back response messages on whether or not a task can be completed. 
#       Or we could share some sort of global status between the server and the plc client

class Button:
    def __init__(self, id, browser):
        self.button = browser.find_element_by_id(id)

    # toggleButton: This clicks a button twice with a time delay in between
    def toggleButton(self):
        self.button.click()
        time.sleep(TIMEDELAY)
        self.button.click()

class PlcClient:
    # init sets up the browser
    def __init__(self):
        self.browser = webdriver.Chrome(CHROMEDRIVERLOCATION)

        # TODO: remove
        self.browser.get('http://localhost:3000/')

    # login: navigates to the login url and enters in password. This opens our custom webpage for the PLC
    def login(self, password):
        self.browser.get(PLCURL)
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
        self.openDoorsButton = Button(OPEN_DOORS_ID, self.browser)
        self.closeDoorsButton = Button(CLOSE_DOORS_ID, self.browser)
        self.emergencyStopButton = Button(EMERGENCY_STOP_ID, self.browser)
        self.extendPadButton = Button(EXTEND_PAD_ID, self.browser)
        self.retractPadButton = Button(RETRACT_PAD_ID, self.browser)
        self.closeRoofButton = Button(CLOSE_ROOF_ID, self.browser)
        self.raisePadButton = Button(RAISE_PAD_ID, self.browser)
        self.lowerPadButton = Button(LOWER_PAD_ID, self.browser)
        self.openRoofButton = Button(OPEN_ROOF_ID, self.browser)
        self.doorOneClosedText = Button(DOOR_ONE_CLOSED_ID, self.browser)
        self.doorTwoClosedText = Button(DOOR_TWO_CLOSED_ID, self.browser)
        self.railRetractedText = Button(RAIL_RETRACTED_ID, self.browser)
        self.roofClosedText = Button(ROOF_CLOSED_ID, self.browser)
        self.liftLoweredText = Button(LIFT_LOWERED_ID, self.browser)
        self.railExtendedText = Button(RAIL_EXTENDED_ID, self.browser)
        self.roofOpenText = Button(ROOF_OPEN_ID, self.browser)
        self.doorTwoOpenText = Button(DOOR_TWO_OPEN_ID, self.browser)
        self.doorOneOpenText = Button(DOOR_ONE_OPEN_ID, self.browser)
        self.liftRaisedText = Button(LIFT_RAISED_ID, self.browser)

    # handleClick: puts each button toggle on a seperate thread so that the application doesnt get hung after every button press
    def handleClick(self, button):
        thread = threading.Thread(target=button.toggleButton)
        thread.daemon = True
        thread.start()

    # Individual operations: These functions handle each of the buttons on the screen
    def emergencyStop(self):
        # TODO: Check sensors
        self.handleClick(self.emergencyStopButton)

    def openDoors(self):
        # TODO: Check sensors
        self.handleClick(self.openDoorsButton)

    def closeDoors(self):
        # TODO: Check sensors
        self.handleClick(self.closeDoorsButton)

    def openRoof(self):
        # TODO: Check sensors
        self.handleClick(self.openRoofButton)

    def closeRoof(self):
        # TODO: Check sensors
        self.handleClick(self.closeRoofButton)

    def extendPad(self):
        # TODO: Check sensors
        self.handleClick(self.extendPadButton)

    def retractPad(self):
        # TODO: Check sensors
        self.handleClick(self.retractPadButton)

    def raisePad(self):
        # TODO: Check sensors
        self.handleClick(self.raisePadButton)

    def lowerPad(self):
        # TODO: Check sensors
        self.handleClick(self.lowerPadButton)

    # Missions
    def bottomDroneMission(self):
        self.openDoors()
        # TODO: Check sensors to see when doors are open
        self.extendPad()
        # TODO: Check sensors to see when pad is fully extended
        # TODO: Send command for drone to take off and wait for drone to come back
        self.retractPad()
        # TODO: Check sensors to see when pad is fully retracted
        self.closeDoors()
        # TODO: Check sensors to see when doors are closed

    def topDroneMission(self):
        self.openRoof()
        # TODO: Check sensors to see when roof is open
        self.raisePad()
        # TODO: Check sensors to see when pad is fully raised
        # TODO: Send command for drone to take off and wait for drone to come back
        self.lowerPad()
        # TODO: Check sensors to see when pad is fully lowerd
        self.closeRoof()
        # TODO: Check sensors to see when roof is closed

    # TODO: Gets the status of all the sensors to relay information back to the server
    def systemStatus(self):
        # systemStatusDict = {
        #     "isOn" : self.isOn,
        #     "isDoorOpen" : self.isDoorOpen,
        #     "isRoofOpen" : self.isRoofOpen,
        #     "isPadExtended" : self.isPadExtended,
        #     "isPadRaised" : self.isPadRaised,
        #     "previousCommand" : self.messagetext
        # }
        # return json.dumps(systemStatusDict)
        pass
    
    # close: needs to be called no matter what to close the browser
    def close(self):
        try:
            self.browser.close()
        except Exception as e: # it might through an exception if the browser has already been closed
            print("PlcClient.close exception:" + str(e))

# This is a fake plc client so that we don't have to be connected to the plc to do normal developing
# It has all of the same functions as PlcClient, but they are empty. This helps us not have to open a 
# browser to the PLC's site everytime we want to test something on the server.
class PlcClientDev:
    
    def __init__(self):
        pass

    def login(self, password):
        pass

    def initButtons(self):
        pass

    def emergencyStop(self):
        pass

    def openDoors(self):
        pass

    def closeDoors(self):
        pass

    def openRoof(self):
        pass

    def closeRoof(self):
        pass

    def extendPad(self):
        pass

    def retractPad(self):
        pass

    def raisePad(self):
        pass

    def lowerPad(self):
        pass

    def bottomDroneMission(self):
        pass

    def topDroneMission(self):
        pass

    def systemStatus(self):
        pass
        
    def close(self):
        pass