from selenium import webdriver
import time
import threading

# Location of chromedriver which can be downloaded from 
# CHROMEDRIVERLOCATION = "C:\\Users\ECE436_18\Desktop\Scripts\chromedriver"
CHROMEDRIVERLOCATION = '/Users/claudia/Desktop/Impress/webscraper/chromedriver'
PLCURL = 'http://192.168.99.3/'
TIMEDELAY = 2

# These come from the HTML
EMERGENCYSTOPID = "EStop"

OPENDOORID = "157910241216714"
ClOSEDOORID = "157910667129821"
OPENROOFID = "157910689748631"
CLOSEROOFID = "157910681743328"
EXTENDPADID = "157910679857925"
RETRACTPADID = "157910680336426"
RAISEPADID = "157910682081829"
LOWERPADID = "157910682381830"

class Button:
    def __init__(self, id, browser):
        self.button = browser.find_element_by_id(id)

    def toggleButton(self):
        self.button.click()
        time.sleep(TIMEDELAY)
        self.button.click()

class PlcClient:
    
    def __init__(self):
        self.browser = webdriver.Chrome(CHROMEDRIVERLOCATION)

        # TODO: remove
        self.browser.get('http://localhost:3000/')

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

    def initButtons(self):
        self.emergencyStopButton = Button(EMERGENCYSTOPID, self.browser)

        self.openDoorsButton = Button(OPENDOORID, self.browser)
        self.closeDoorsButton = Button(ClOSEDOORID, self.browser)
        self.openRoofButton = Button(OPENROOFID, self.browser)
        self.closeRoofButton = Button(CLOSEROOFID, self.browser)
        self.extendPadButton = Button(EXTENDPADID, self.browser)
        self.retractPadButton = Button(RETRACTPADID, self.browser)
        self.raisePadButton = Button(RAISEPADID, self.browser)
        self.lowerPadButton = Button(LOWERPADID, self.browser)

    def handleClick(self, button):
        thread = threading.Thread(target=button.toggleButton)
        thread.daemon = True
        thread.start()

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
        
    def close(self):
        self.browser.close()

# This is a fake plc client so that we don't have to be connected to the plc to do normal developing
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
        
    def close(self):
        pass