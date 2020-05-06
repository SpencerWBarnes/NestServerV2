import sys
import time
import json
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from flask import Flask
import requests
from threading import Thread
import StringConstants as strings

IP_ADDRESS = '192.168.0.102'
VIDEO_COMMAND_PORT = 8000
IMAGE_PORT = 8001
BUFFER_SIZE = 1024

######### WebPage: the web engine that displays webpage content #########
class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)

######### Password Override Dialog Box #########
class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(PasswordDialog, self).__init__(parent)
        self.shouldSendPasswordOverride = False
        self.commandMessage = ""
        
        # Labels and Line edits
        self.passwordOverrideLabel = QLabel("Enter override password: ")
        self.messageToSendLabel = QLabel("")
        self.passwordLineEdit = QLineEdit()
        
        # Buttons
        self.submitButton = QPushButton("Submit")
        self.openDoorsButton = QPushButton("Open Doors")
        self.closeDoorsButton = QPushButton("Close Doors")
        self.openRoofButton = QPushButton("Open Roof")
        self.closeRoofButton = QPushButton("Close Roof")
        self.extendPadButton = QPushButton("Extend Pad")
        self.retractPadButton = QPushButton("Retract Pad")
        self.raisePadButton = QPushButton("Raise Pad")
        self.lowerPadButton = QPushButton("Lower Pad")

        # Button on click listeners
        self.openDoorsButton.clicked.connect(self.OpenDoors)
        self.closeDoorsButton.clicked.connect(self.CloseDoors)
        self.openRoofButton.clicked.connect(self.OpenRoof)
        self.closeRoofButton.clicked.connect(self.CloseRoof)
        self.extendPadButton.clicked.connect(self.ExtendPad)
        self.retractPadButton.clicked.connect(self.RetractPad)
        self.raisePadButton.clicked.connect(self.RaisePad)
        self.lowerPadButton.clicked.connect(self.LowerPad)
        self.submitButton.clicked.connect(self.Submit)

        # Button Layout
        buttonlayout = QGridLayout()
        buttonlayout.addWidget(self.openDoorsButton, 1, 1)
        buttonlayout.addWidget(self.closeDoorsButton, 1, 2)
        buttonlayout.addWidget(self.openRoofButton, 2, 1)
        buttonlayout.addWidget(self.closeRoofButton, 2, 2)
        buttonlayout.addWidget(self.extendPadButton, 3, 1)
        buttonlayout.addWidget(self.retractPadButton, 3, 2)
        buttonlayout.addWidget(self.raisePadButton, 4, 1)
        buttonlayout.addWidget(self.lowerPadButton, 4, 2)

        # Main Layout
        layout = QVBoxLayout()
        layout.addWidget(self.passwordOverrideLabel)
        layout.addWidget(self.messageToSendLabel)
        layout.addWidget(self.passwordLineEdit)
        layout.addWidget(self.submitButton)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)

    def disableButtons(self):
        self.openDoorsButton.setDisabled(True)
        self.closeDoorsButton.setDisabled(True)
        self.openRoofButton.setDisabled(True)
        self.closeRoofButton.setDisabled(True)
        self.extendPadButton.setDisabled(True)
        self.retractPadButton.setDisabled(True)
        self.raisePadButton.setDisabled(True)
        self.lowerPadButton.setDisabled(True)

    def OpenDoors(self):
        self.commandMessage = "openDoors"
        self.messageToSendLabel.setText("Message to be sent: openDoors")
        self.disableButtons()

    def CloseDoors(self):
        self.commandMessage = "closeDoors"
        self.messageToSendLabel.setText("Message to be sent: closeDoors")
        self.disableButtons()

    def OpenRoof(self):
        self.commandMessage = "openRoof"
        self.messageToSendLabel.setText("Message to be sent: openRoof")
        self.disableButtons()

    def CloseRoof(self):
        self.commandMessage = "closeRoof"
        self.messageToSendLabel.setText("Message to be sent: closeRoof")
        self.disableButtons()

    def ExtendPad(self):
        self.commandMessage = "extendPad"
        self.messageToSendLabel.setText("Message to be sent: extendPad")
        self.disableButtons()

    def RetractPad(self):
        self.commandMessage = "retractPad"
        self.messageToSendLabel.setText("Message to be sent: retractPad")
        self.disableButtons()

    def RaisePad(self):
        self.commandMessage = "raisePad"
        self.messageToSendLabel.setText("Message to be sent: raisePad")
        self.disableButtons()

    def LowerPad(self):
        self.commandMessage = "lowerPad"
        self.messageToSendLabel.setText("Message to be sent: lowerPad")
        self.disableButtons()

    # Notifies the main application that there should be a password override through shouldSendPasswordOverride
    def Submit(self):
        self.password = str(self.passwordLineEdit.text())
        self.message = str(self.commandMessage)
        self.shouldSendPasswordOverride = True
        self.done(1)

######### Main UI #########
class Form():
    def init_gui(self, application, width=800, height=800, window_title="Nest Client", argv=None):
        if argv is None:
            argv = sys.argv
        
        # Some important variables
        self.isOn = False
        self.isDoorOpen = False
        self.isRoofOpen = False
        self.isPadExtended = False
        self.isPadRaised = False
        self.videoSock = None
        self.isConnected = False
        self.messagetext = ""

        self.baseUrl = ""

        # Application Level
        global qtapp
        qtapp = QApplication(argv)

        # Main Window Level
        window = QWidget()
        window.resize(width, height)
        window.setWindowTitle(window_title)

        # WebView Level
        self.webView = QtWebEngineWidgets.QWebEngineView(window)
        self.webView.setMinimumHeight(520)
        self.webView2 = QtWebEngineWidgets.QWebEngineView(window)
        self.webView2.setMinimumHeight(520)

        # Widgets Level
        self.ipLabel = QLabel('Server IP:')
        self.ipLineEdit = QLineEdit(IP_ADDRESS)
        self.portLabel = QLabel('Port:')
        self.portLineEdit = QLineEdit(str(VIDEO_COMMAND_PORT))
        self.submitConnect = QPushButton('Connect')

        # Labels
        self.statusLabel = QLabel("Waiting for input...")
        self.powerStatusLabel = QLabel("System Power: OFF")
        self.doorStatusLabel = QLabel("Doors: CLOSED")
        self.roofStatusLabel = QLabel("Roof: CLOSED")
        self.roofPadStatusLabel = QLabel("Top Pad: LOWERED")
        self.backPadStatusLabel = QLabel("Back Pad: RETRACTED")
        self.missionLabel = QLabel("Run mission")

        # Buttons
        self.systemPowerButton = QPushButton("System Power")
        self.emergencyStopButton = QPushButton("Emergency Stop")
        self.passwordOverrideButton = QPushButton("Override")
        self.openDoorsButton = QPushButton("Open Doors")
        self.closeDoorsButton = QPushButton("Close Doors")
        self.openRoofButton = QPushButton("Open Roof")
        self.closeRoofButton = QPushButton("Close Roof")
        self.extendPadButton = QPushButton("Extend Pad")
        self.retractPadButton = QPushButton("Retract Pad")
        self.raisePadButton = QPushButton("Raise Pad")
        self.lowerPadButton = QPushButton("Lower Pad")
        self.bottomDroneMissionButton = QPushButton("Bottom Drone Mission")
        self.topDroneMissionButton = QPushButton("Top Drone Mission")

        self.emergencyStopButton.setDisabled(True)
        self.passwordOverrideButton.setDisabled(True)
        self.openDoorsButton.setDisabled(True)
        self.closeDoorsButton.setDisabled(True)
        self.openRoofButton.setDisabled(True)
        self.closeRoofButton.setDisabled(True)
        self.extendPadButton.setDisabled(True)
        self.retractPadButton.setDisabled(True)
        self.raisePadButton.setDisabled(True)
        self.lowerPadButton.setDisabled(True)
        self.bottomDroneMissionButton.setDisabled(True)
        self.topDroneMissionButton.setDisabled(True)

        # Button on Click listeners
        self.submitConnect.clicked.connect(self.connection)
        self.systemPowerButton.clicked.connect(self.SystemPower)
        self.emergencyStopButton.clicked.connect(self.EmergencyStop)
        self.passwordOverrideButton.clicked.connect(self.PasswordOverride)
        self.openDoorsButton.clicked.connect(self.OpenDoors)
        self.closeDoorsButton.clicked.connect(self.CloseDoors)
        self.openRoofButton.clicked.connect(self.OpenRoof)
        self.closeRoofButton.clicked.connect(self.CloseRoof)
        self.extendPadButton.clicked.connect(self.ExtendPad)
        self.retractPadButton.clicked.connect(self.RetractPad)
        self.raisePadButton.clicked.connect(self.RaisePad)
        self.lowerPadButton.clicked.connect(self.LowerPad)
        self.bottomDroneMissionButton.clicked.connect(lambda: self.RunDroneMission(strings.MESSAGE_BOTTOM_DRONE_MISSION))
        self.topDroneMissionButton.clicked.connect(lambda: self.RunDroneMission(strings.MESSAGE_TOP_DRONE_MISSION))

        # Layouts
        clientlayout = QGridLayout()
        clientlayout.addWidget(self.ipLabel, 0, 0)
        clientlayout.addWidget(self.ipLineEdit, 0, 1)
        clientlayout.addWidget(self.portLabel, 0, 2)
        clientlayout.addWidget(self.portLineEdit, 0, 3)
        clientlayout.addWidget(self.submitConnect, 0, 4)

        # Layouts - Buttons
        buttonlayout = QGridLayout()
        buttonlayout.addWidget(self.powerStatusLabel, 0, 0)
        buttonlayout.addWidget(self.systemPowerButton, 0, 1)
        buttonlayout.addWidget(self.emergencyStopButton, 0, 2)
        buttonlayout.addWidget(self.passwordOverrideButton, 0, 3)
        buttonlayout.addWidget(self.doorStatusLabel, 1, 0)
        buttonlayout.addWidget(self.openDoorsButton, 1, 1)
        buttonlayout.addWidget(self.closeDoorsButton, 1, 2)
        buttonlayout.addWidget(self.roofStatusLabel, 2, 0)
        buttonlayout.addWidget(self.openRoofButton, 2, 1)
        buttonlayout.addWidget(self.closeRoofButton, 2, 2)
        buttonlayout.addWidget(self.backPadStatusLabel, 3, 0)
        buttonlayout.addWidget(self.extendPadButton, 3, 1)
        buttonlayout.addWidget(self.retractPadButton, 3, 2)
        buttonlayout.addWidget(self.roofPadStatusLabel, 4, 0)
        buttonlayout.addWidget(self.raisePadButton, 4, 1)
        buttonlayout.addWidget(self.lowerPadButton, 4, 2)
        buttonlayout.addWidget(self.missionLabel, 5, 0)
        buttonlayout.addWidget(self.bottomDroneMissionButton, 5, 1)
        buttonlayout.addWidget(self.topDroneMissionButton, 5, 2)

        # WebPage Layout
        vidLayout = QHBoxLayout()
        page = WebPage('http://' + IP_ADDRESS + ':{}'.format(VIDEO_COMMAND_PORT)) 
        self.webView.setPage(page)
        self.webView.setMinimumHeight(730)
        self.webView.setMinimumWidth(600)
        vidLayout.addWidget(self.webView)

        page2 = WebPage('http://' + IP_ADDRESS + ':{}'.format(IMAGE_PORT)) 
        self.webView2.setPage(page2)
        self.webView2.setMaximumHeight(730)
        self.webView2.setMaximumWidth(440)
        vidLayout.addWidget(self.webView2)

        # Layouts - Setting layouts
        layout = QGridLayout()
        layout.addLayout(vidLayout, 3, 0)
        layout.addLayout(clientlayout, 0, 0)
        layout.addLayout(buttonlayout, 1, 0)
        layout.addWidget(self.statusLabel, 2, 0)

        window.setLayout(layout)

        

        # Some variables needed for everything else
        self.pollingThread = Thread(target=self.poll)
        self.pollingThread.daemon = True

        window.showMaximized()
        return qtapp.exec_()


    ######### Listening and reciving data #########

    # poll: get an update about the state of the nest every second
    def poll(self):
        while (1):
            self.systemDiagnostic()
            time.sleep(1)
    
    # systemDiagnostic: asks the server for a json response of the status of the nest and refreshes the UI
    def systemDiagnostic(self):

        # Send Message
        data = self.sendData(strings.MESSAGE_SYSTEM_STATUS)

        # Parse Message
        try:
            # Strip json and convert to dictionary
            print(data)
            dataform = data.strip("'<>() ").replace('\'', '\"')
            jsonData = json.loads(dataform)

            # Get status
            self.isOn = jsonData['isOn']
            self.isDoorOpen = jsonData['isDoorOpen']
            self.isRoofOpen = jsonData['isRoofOpen']
            self.isPadExtended = jsonData['isPadExtended']
            self.isPadRaised = jsonData['isPadRaised']
            self.statusLabel.setText("Last command: " + jsonData['previousCommand'])

            # Labels
            if(self.isDoorOpen):
                self.doorStatusLabel.setText("Doors: OPEN")
            else:
                self.doorStatusLabel.setText("Doors: CLOSED")

            if(self.isRoofOpen):
                self.roofStatusLabel.setText("Roof: OPEN")
            else:
                self.roofStatusLabel.setText("Roof: CLOSED")

            if(self.isPadExtended):
                self.backPadStatusLabel.setText("Back Pad: EXTENDED")
            else:
                self.backPadStatusLabel.setText("Back Pad: RETRACTED")

            if(self.isPadRaised):
                self.roofPadStatusLabel.setText("Top Pad: RAISED")
            else:
                self.roofPadStatusLabel.setText("Top Pad: LOWERED")
            
            # Top Buttons
            if(self.isOn):
                self.powerStatusLabel.setText("System Power: ON")
                self.emergencyStopButton.setDisabled(False)
                self.passwordOverrideButton.setDisabled(False)
            else:
                self.powerStatusLabel.setText("System Power: OFF")
                self.emergencyStopButton.setDisabled(True)
                self.passwordOverrideButton.setDisabled(True)

            # Doors
            if(self.isOn and not self.isDoorOpen):
                self.openDoorsButton.setDisabled(False)
            else: 
                self.openDoorsButton.setDisabled(True)

            if(self.isOn and self.isDoorOpen and not self.isPadExtended):
                self.closeDoorsButton.setDisabled(False)
            else: 
                self.closeDoorsButton.setDisabled(True)

            # Roof
            if(self.isOn and not self.isRoofOpen):
                self.openRoofButton.setDisabled(False)
            else: 
                self.openRoofButton.setDisabled(True)

            if(self.isOn and self.isRoofOpen and not self.isPadRaised):
                self.closeRoofButton.setDisabled(False)
            else: 
                self.closeRoofButton.setDisabled(True)

            # Pad Extend
            if(self.isOn and self.isDoorOpen and not self.isPadExtended):
                self.extendPadButton.setDisabled(False)
            else: 
                self.extendPadButton.setDisabled(True)

            if(self.isOn and self.isPadExtended):
                self.retractPadButton.setDisabled(False)
            else: 
                self.retractPadButton.setDisabled(True)

            # Pad Raise
            if(self.isOn and self.isRoofOpen and not self.isPadRaised):
                self.raisePadButton.setDisabled(False)
            else: 
                self.raisePadButton.setDisabled(True)

            if(self.isOn and self.isPadRaised):
                self.lowerPadButton.setDisabled(False)
            else: 
                self.lowerPadButton.setDisabled(True)

            # Missions
            if(self.isOn and not self.isDoorOpen) and (self.isOn and not self.isRoofOpen):
                self.bottomDroneMissionButton.setDisabled(False)
                self.topDroneMissionButton.setDisabled(False)
            else: 
                self.bottomDroneMissionButton.setDisabled(True)
                self.topDroneMissionButton.setDisabled(True)

        except:
            print("impropper data: " + data)

    
    def connection(self):
        if (self.isConnected == False):
            try:
                self.isConnected = True
                self.baseUrl = 'http://' + self.ipLineEdit.text() + ':{}'.format(VIDEO_COMMAND_PORT)

                self.sendData(strings.MESSAGE_CONNECTION_TEST)

                # Start checking for systemDiagnostic
                self.pollingThread.start()

                # WebPage Level
                print("GETTING WEBPAGE FROM: " + self.baseUrl)
                page = WebPage(self.baseUrl)
                page.home()
                self.webView.setUrl(QUrl(self.baseUrl))
                
            except OSError as e:
                print(e)
                self.statusLabel.setText("Invalid IP")
                self.submitConnect.setDisabled(False)
    
    # sendData: sends data to server
    def sendData(self, data, password = ""):
        r = requests.get(self.baseUrl + "/" + data, headers={"auth": password})
        data  = r.text

        if "Error" in data:
            print("uh oh error!")

        return data

    ######### Button Listeners #########
    def SystemPower(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_SYSTEM_POWER)
            self.powerStatusLabel.setText(self.messagetext)
            if self.messagetext == "System Power: ON":
                self.emergencyStopButton.setDisabled(False)
                self.passwordOverrideButton.setDisabled(False)
                self.openDoorsButton.setDisabled(False)
                self.openRoofButton.setDisabled(False)
            else:
                self.emergencyStopButton.setDisabled(True)
                self.passwordOverrideButton.setDisabled(True)
                self.openDoorsButton.setDisabled(True)
                self.openRoofButton.setDisabled(True)
                self.extendPadButton.setDisabled(True)
                self.raisePadButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def EmergencyStop(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_EMERGENCY_STOP)
            self.powerStatusLabel.setText(self.messagetext)
            self.emergencyStopButton.setDisabled(True)
            self.openDoorsButton.setDisabled(True)
            self.closeDoorsButton.setDisabled(True)
            self.openRoofButton.setDisabled(True)
            self.closeRoofButton.setDisabled(True)
            self.extendPadButton.setDisabled(True)
            self.retractPadButton.setDisabled(True)
            self.raisePadButton.setDisabled(True)
            self.lowerPadButton.setDisabled(True)
            self.bottomDroneMissionButton.setDisabled(True)
            self.topDroneMissionButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def PasswordOverride(self):
        if self.isConnected:
            self.dialog = PasswordDialog()
            self.dialog.exec()
            if (self.dialog.shouldSendPasswordOverride == True):
                password = self.dialog.password
                message = self.dialog.message
                response = self.sendData(message, password=password)
                self.systemDiagnostic()

    def OpenDoors(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_OPEN_DOORS)
            self.doorStatusLabel.setText(self.messagetext)
            self.openDoorsButton.setDisabled(True)
            self.closeDoorsButton.setDisabled(False)
            self.extendPadButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def CloseDoors(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_CLOSE_DOORS)
            self.doorStatusLabel.setText(self.messagetext)
            self.closeDoorsButton.setDisabled(True)
            self.openDoorsButton.setDisabled(False)
            self.extendPadButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def OpenRoof(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_OPEN_ROOF)
            self.roofStatusLabel.setText(self.messagetext)
            self.openRoofButton.setDisabled(True)
            self.closeRoofButton.setDisabled(False)
            self.raisePadButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def CloseRoof(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_CLOSE_ROOF)
            self.roofStatusLabel.setText(self.messagetext)
            self.closeRoofButton.setDisabled(True)
            self.openRoofButton.setDisabled(False)
            self.raisePadButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def ExtendPad(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_EXTEND_PAD)
            self.backPadStatusLabel.setText(self.messagetext)
            self.extendPadButton.setDisabled(True)
            self.retractPadButton.setDisabled(False)
            self.closeDoorsButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def RetractPad(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_RETRACT_PAD)
            self.backPadStatusLabel.setText(self.messagetext)
            self.retractPadButton.setDisabled(True)
            self.extendPadButton.setDisabled(False)
            self.closeDoorsButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def RaisePad(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_RAISE_PAD)
            self.roofPadStatusLabel.setText(self.messagetext)
            self.raisePadButton.setDisabled(True)
            self.lowerPadButton.setDisabled(False)
            self.closeRoofButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def LowerPad(self):
        if self.isConnected:
            self.messagetext = self.sendData(strings.MESSAGE_LOWER_PAD)
            self.roofPadStatusLabel.setText(self.messagetext)
            self.lowerPadButton.setDisabled(True)
            self.raisePadButton.setDisabled(False)
            self.closeRoofButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def RunDroneMission(self, missionMessage):
        if self.isConnected:
            self.messagetext = self.sendData(missionMessage)
            self.missionLabel.setText(self.messagetext)
            self.openDoorsButton.setDisabled(True)
            self.closeDoorsButton.setDisabled(True)
            self.openRoofButton.setDisabled(True)
            self.closeRoofButton.setDisabled(True)
            self.extendPadButton.setDisabled(True)
            self.retractPadButton.setDisabled(True)
            self.raisePadButton.setDisabled(True)
            self.lowerPadButton.setDisabled(True)
            self.bottomDroneMissionButton.setDisabled(True)
            self.topDroneMissionButton.setDisabled(True)
        else:
            self.label.setText("Please Connect First")


######### Running client #########
if __name__ == '__main__':
    app = Flask(__name__)
    client =  Form()
    client.init_gui(app, width=800, height=800, window_title="Nest Client", argv=None)
