import sys
import time
import json
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from flask import Flask
import socket
from threading import Thread

IP_ADDRESS = '192.168.0.8'
TCP_PORT = 8888
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
        self.bottomDroneMissionButton.setDisabled(True)
        self.topDroneMissionButton.setDisabled(True)

    def OpenDoors(self):
        self.commandMessage = "openDoorsButton"
        self.messageToSendLabel.setText("Message to be sent: openDoorsButton")
        self.disableButtons()

    def CloseDoors(self):
        self.commandMessage = "closeDoorsButton"
        self.messageToSendLabel.setText("Message to be sent: closeDoorsButton")
        self.disableButtons()

    def OpenRoof(self):
        self.commandMessage = "openRoofButton"
        self.messageToSendLabel.setText("Message to be sent: openRoofButton")
        self.disableButtons()

    def CloseRoof(self):
        self.commandMessage = "closeRoofButton"
        self.messageToSendLabel.setText("Message to be sent: closeRoofButton")
        self.disableButtons()

    def ExtendPad(self):
        self.commandMessage = "extendPadButton"
        self.messageToSendLabel.setText("Message to be sent: extendPadButton")
        self.disableButtons()

    def RetractPad(self):
        self.commandMessage = "retractPadButton"
        self.messageToSendLabel.setText("Message to be sent: retractPadButton")
        self.disableButtons()

    def RaisePad(self):
        self.commandMessage = "raisePadButton"
        self.messageToSendLabel.setText("Message to be sent: raisePadButton")
        self.disableButtons()

    def LowerPad(self):
        self.commandMessage = "lowerPadButton"
        self.messageToSendLabel.setText("Message to be sent: lowerPadButton")
        self.disableButtons()

    # Notifies the main application that there should be a password override through shouldSendPasswordOverride
    def Submit(self):
        self.passwordmessage = self.passwordLineEdit.text()
        self.servermessage = str(self.passwordmessage) + ": " + str(self.commandMessage)
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

        # Widgets Level
        self.ipLabel = QLabel('Server IP:')
        self.ipLineEdit = QLineEdit(IP_ADDRESS)
        self.portLabel = QLabel('Port:')
        self.portLineEdit = QLineEdit(str(TCP_PORT))
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
        self.bottomDroneMissionButton.clicked.connect(lambda: self.RunDroneMission("bottomDroneMission"))
        self.topDroneMissionButton.clicked.connect(lambda: self.RunDroneMission("topDroneMission"))

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

        # Layouts - Setting layouts
        layout = QGridLayout()
        layout.addLayout(clientlayout, 0, 0)
        layout.addLayout(buttonlayout, 1, 0)
        layout.addWidget(self.statusLabel, 2, 0)
        layout.addWidget(self.webView, 3, 0)

        window.setLayout(layout)

        # WebPage Level
        page = WebPage('')
        page.home()
        self.webView.setPage(page)

        # Some variables needed for everything else
        self.pollingThread = Thread(target=self.poll)
        self.pollingThread.daemon = True

        # Setting up the socket to send commands
        self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        window.show()
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
        data = self.sendData("systemStatus")

        # Parse Message
        try:
            # Strip json and convert to dictionary
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
                print ((self.ipLineEdit.text(), int(self.portLineEdit.text())))
                self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.commandSock.connect((self.ipLineEdit.text(), int(self.portLineEdit.text())))
                self.submitConnect.setDisabled(True)
            except Exception as e:
                self.statusLabel.setText(str(e))
                print(e)
                return

            try:
                self.isConnected = True

                self.sendData("Connection Test")

                # Start checking for systemDiagnostic
                self.pollingThread.start()

                # WebPage Level
                text = 'http://' + self.ipLineEdit.text() + ':{}'.format(8000)
                print("GETTING WEBPAGE FROM: " + text)
                page = WebPage(text)
                page.home()
                self.webView.setUrl(QUrl(text))
                
            except OSError as e:
                print(e)
                self.statusLabel.setText("Invalid IP")
                self.submitConnect.setDisabled(False)
    
    # sendData: sends data to server
    def sendData(self, data):
        self.commandSock.sendall(data.encode())
        data = self.commandSock.recv(BUFFER_SIZE)
        data = data.decode()

        if "Error" in data:
            print("uh oh error!")

        return data

    ######### Button Listeners #########
    def SystemPower(self):
        if self.isConnected:
            self.messagetext = self.sendData("systemPower")
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
            self.messagetext = self.sendData("emergencyStop")
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
        else:
            self.statusLabel.setText("Please Connect First")

    def PasswordOverride(self):
        if self.isConnected:
            self.dialog = PasswordDialog()
            self.dialog.exec()
            if (self.dialog.shouldSendPasswordOverride == True):
                self.passwordmessage = self.dialog.servermessage
                response = self.sendData(self.passwordmessage)
                self.systemDiagnostic()

    def OpenDoors(self):
        if self.isConnected:
            self.messagetext = self.sendData("openDoors")
            self.doorStatusLabel.setText(self.messagetext)
            self.openDoorsButton.setDisabled(True)
            self.closeDoorsButton.setDisabled(False)
            self.extendPadButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def CloseDoors(self):
        if self.isConnected:
            self.messagetext = self.sendData("closeDoors")
            self.doorStatusLabel.setText(self.messagetext)
            self.closeDoorsButton.setDisabled(True)
            self.openDoorsButton.setDisabled(False)
            self.extendPadButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def OpenRoof(self):
        if self.isConnected:
            self.messagetext = self.sendData("openRoof")
            self.roofStatusLabel.setText(self.messagetext)
            self.openRoofButton.setDisabled(True)
            self.closeRoofButton.setDisabled(False)
            self.raisePadButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def CloseRoof(self):
        if self.isConnected:
            self.messagetext = self.sendData("closeRoof")
            self.roofStatusLabel.setText(self.messagetext)
            self.closeRoofButton.setDisabled(True)
            self.openRoofButton.setDisabled(False)
            self.raisePadButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def ExtendPad(self):
        if self.isConnected:
            self.messagetext = self.sendData("extendPad")
            self.backPadStatusLabel.setText(self.messagetext)
            self.extendPadButton.setDisabled(True)
            self.retractPadButton.setDisabled(False)
            self.closeDoorsButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def RetractPad(self):
        if self.isConnected:
            self.messagetext = self.sendData("retractPad")
            self.backPadStatusLabel.setText(self.messagetext)
            self.retractPadButton.setDisabled(True)
            self.extendPadButton.setDisabled(False)
            self.closeDoorsButton.setDisabled(False)
        else:
            self.statusLabel.setText("Please Connect First")

    def RaisePad(self):
        if self.isConnected:
            self.messagetext = self.sendData("raisePad")
            self.roofPadStatusLabel.setText(self.messagetext)
            self.raisePadButton.setDisabled(True)
            self.lowerPadButton.setDisabled(False)
            self.closeRoofButton.setDisabled(True)
        else:
            self.statusLabel.setText("Please Connect First")

    def LowerPad(self):
        if self.isConnected:
            self.messagetext = self.sendData("lowerPad")
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
            self.closeDoorsButton.setDisabled(False)
            self.openRoofButton.setDisabled(False)
            self.closeRoofButton.setDisabled(True)
            self.extendPadButton.setDisabled(False)
            self.retractPadButton.setDisabled(False)
            self.raisePadButton.setDisabled(False)
            self.lowerPadButton.setDisabled(False)
        else:
            self.label.setText("Please Connect First")


######### Running client #########
if __name__ == '__main__':
    app = Flask(__name__)
    client =  Form()
    client.init_gui(app, width=800, height=800, window_title="Nest Client", argv=None)
