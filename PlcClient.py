from selenium import webdriver
import time
import threading

# Location of chromedriver which can be downloaded from https://sites.google.com/a/chromium.org/chromedriver/ 
# download this and copy and paste where that file is here vvvv
# CHROMEDRIVERLOCATION = "C:\\Users\ECE436_18\Desktop\Scripts\chromedriver"
CHROMEDRIVERLOCATION = '/Users/claudia/Desktop/Impress/webscraper/chromedriver'
PLCURL = 'http://192.168.99.3/'
TIMEDELAY = 2

# These come from the ID's of elements in the HTML
EMERGENCYSTOPBUTTON = "157910667599022"

OPENDOORBUTTON = "157910241216714"
CLOSEDOORBUTTON = "157910667129821"
OPENROOFBUTTON = "157910689748631"
CLOSEROOFBUTTON = "157910681743328"
EXTENDPADBUTTON = "157910679857925"
RETRACTPADBUTTON = "157910680336426"
RAISEPADBUTTON = "157910682081829"
LOWERPADBUTTON = "157910682381830"

# DOORSOPENSENSOR
# DOORSCLOSEDSENSOR
# ROOFOPENSENSOR
# ROOFCLOSEDSENSOR

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
        # self.browser.get('http://localhost:3000/')

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
        self.emergencyStopButton = Button(EMERGENCYSTOPBUTTON, self.browser)

        self.openDoorsButton = Button(OPENDOORBUTTON, self.browser)
        self.closeDoorsButton = Button(CLOSEDOORBUTTON, self.browser)
        self.openRoofButton = Button(OPENROOFBUTTON, self.browser)
        self.closeRoofButton = Button(CLOSEROOFBUTTON, self.browser)
        self.extendPadButton = Button(EXTENDPADBUTTON, self.browser)
        self.retractPadButton = Button(RETRACTPADBUTTON, self.browser)
        self.raisePadButton = Button(RAISEPADBUTTON, self.browser)
        self.lowerPadButton = Button(LOWERPADBUTTON, self.browser)

    # handleClick: puts each button toggle on a seperate thread so that the application doesnt get hung after every button press
    def handleClick(self, button):
        thread = threading.Thread(target=button.toggleButton)
        thread.daemon = True
        thread.start()

    # Individual operations: These functions handle each of the buttons on the screen
    def emergencyStop(self):
        self.handleClick(self.emergencyStopButton)

    def openDoors(self):
        self.handleClick(self.openDoorsButton)

    def closeDoors(self):
        self.handleClick(self.closeDoorsButton)

    def openRoof(self):
        self.handleClick(self.openRoofButton)

    def closeRoof(self):
        self.handleClick(self.closeDoorsButton)

    def extendPad(self):
        self.handleClick(self.extendPadButton)

    def retractPad(self):
        self.handleClick(self.retractPadButton)

    def raisePad(self):
        self.handleClick(self.raisePadButton)

    def lowerPad(self):
        self.handleClick(self.lowerPadButton)

    # Missions
    def bottomDroneMission(self):
        self.openDoors()
        # Check sensors to see when doors are open
        self.extendPad()
        # Check sensors to see when pad is fully extended
        # Send command for drone to take off and wait for drone to come back
        self.retractPad()
        # Check sensors to see when pad is fully retracted
        self.closeDoors()
        # Check sensors to see when doors are closed

    def topDroneMission(self):
        self.openRoof()
        # Check sensors to see when roof is open
        self.raisePad()
        # Check sensors to see when pad is fully raised
        # Send command for drone to take off and wait for drone to come back
        self.lowerPad()
        # Check sensors to see when pad is fully lowerd
        self.closeRoof()
        # Check sensors to see when roof is closed

    # Gets the status of all the sensors to relay information back to the server
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