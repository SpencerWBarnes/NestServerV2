from selenium import webdriver
import time

# Location of chromedriver which can be downloaded from 
# CHROMEDRIVERLOCATION = "C:\\Users\ECE436_18\Desktop\Scripts\chromedriver"
CHROMEDRIVERLOCATION = '/Users/claudia/Desktop/Impress/webscraper/chromedriver'
PLCURL = 'http://192.168.99.3/'
TIMEDELAY = 2

# These come from the HTML
EMERGENCYSTOPID = ""
# OPENDOORID = "submit"
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
        # self.browser.get('http://localhost:3000/public/dummy.html')

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
        # self.emergencyStopButton = Button(EMERGENCYSTOPID, self.browser)

        self.openDoorsButton = Button(OPENDOORID, self.browser)
        # self.closeDoorsButton = Button(ClOSEDOORID, self.browser)
        # self.openRoofButton = Button(OPENROOFID, self.browser)
        # self.closeRoofButton = Button(CLOSEROOFID, self.browser)
        # self.extendPadButton = Button(EXTENDPADID, self.browser)
        # self.retractPadButton = Button(RETRACTPADID, self.browser)
        # self.raisePadButton = Button(RAISEPADID, self.browser)
        # self.lowerPadButton = Button(LOWERPADID, self.browser)

    def close(self):
        self.browser.close()