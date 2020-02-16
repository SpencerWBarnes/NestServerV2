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
        self.serverLabel = QLabel('Server IP:')
        self.ipLineEdit = QLineEdit("192.168.0.13")
        self.portLineEdit = QLineEdit("8888")
        self.submitConnect = QPushButton("Connect")

        # Labels
        self.label = QLabel("Waiting for input...")
        self.systemStatus = QLabel("System Power: OFF")
        self.doorStatus = QLabel("Doors: CLOSED")
        self.roofStatus = QLabel("Roof: CLOSED")
        self.roofPadStatus = QLabel("Top Pad: LOWERED")
        self.backPadStatus = QLabel("Back Pad: RETRACTED")

        # Buttons
        self.systemPower = QPushButton("System Power")
        self.emergencyStop = QPushButton("Emergency Stop")
        self.passwordoverride = QPushButton("Override")
        self.openDoors = QPushButton("Open Doors")
        self.closeDoors = QPushButton("Close Doors")
        self.openRoof = QPushButton("Open Roof")
        self.closeRoof = QPushButton("Close Roof")
        self.extendPad = QPushButton("Extend Pad")
        self.retractPad = QPushButton("Retract Pad")
        self.raisePad = QPushButton("Raise Pad")
        self.lowerPad = QPushButton("Lower Pad")

        self.emergencyStop.setDisabled(True)
        self.passwordoverride.setDisabled(True)
        self.openDoors.setDisabled(True)
        self.closeDoors.setDisabled(True)
        self.openRoof.setDisabled(True)
        self.closeRoof.setDisabled(True)
        self.extendPad.setDisabled(True)
        self.retractPad.setDisabled(True)
        self.raisePad.setDisabled(True)
        self.lowerPad.setDisabled(True)

        # Button on Click listeners
        self.submitConnect.clicked.connect(self.connection)
        self.systemPower.clicked.connect(self.SystemPower)
        self.emergencyStop.clicked.connect(self.EmergencyStop)
        self.passwordoverride.clicked.connect(self.PasswordOverride)
        self.openDoors.clicked.connect(self.OpenDoors)
        self.closeDoors.clicked.connect(self.CloseDoors)
        self.openRoof.clicked.connect(self.OpenRoof)
        self.closeRoof.clicked.connect(self.CloseRoof)
        self.extendPad.clicked.connect(self.ExtendPad)
        self.retractPad.clicked.connect(self.RetractPad)
        self.raisePad.clicked.connect(self.RaisePad)
        self.lowerPad.clicked.connect(self.LowerPad)

        # Layouts
        clientlayout = QVBoxLayout()
        clientlayout.addWidget(self.serverLabel)
        clientlayout.addWidget(self.ipLineEdit)
        clientlayout.addWidget(self.portLineEdit)
        clientlayout.addWidget(self.submitConnect)

        # Layouts - Buttons
        buttonlayout = QGridLayout()
        buttonlayout.addWidget(self.systemStatus, 0, 0)
        buttonlayout.addWidget(self.systemPower, 0, 1)
        buttonlayout.addWidget(self.emergencyStop, 0, 2)
        buttonlayout.addWidget(self.passwordoverride, 0, 3)
        buttonlayout.addWidget(self.doorStatus, 1, 0)
        buttonlayout.addWidget(self.openDoors, 1, 1)
        buttonlayout.addWidget(self.closeDoors, 1, 2)
        buttonlayout.addWidget(self.roofStatus, 2, 0)
        buttonlayout.addWidget(self.openRoof, 2, 1)
        buttonlayout.addWidget(self.closeRoof, 2, 2)
        buttonlayout.addWidget(self.backPadStatus, 3, 0)
        buttonlayout.addWidget(self.extendPad, 3, 1)
        buttonlayout.addWidget(self.retractPad, 3, 2)
        buttonlayout.addWidget(self.roofPadStatus, 4, 0)
        buttonlayout.addWidget(self.raisePad, 4, 1)
        buttonlayout.addWidget(self.lowerPad, 4, 2)

        # Layouts - Setting layouts
        layout = QGridLayout()
        layout.addLayout(clientlayout, 0, 0)
        layout.addLayout(buttonlayout, 1, 0)
        layout.addWidget(self.label, 2, 0)
        layout.addWidget(self.webView, 3, 0)

        window.setLayout(layout)

        # WebPage Level
        page = WebPage('http://www.google.com')
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
        message = self.sendData("systemStatus")
        message.decode()

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

            # Labels
            if(self.isDoorOpen):
                self.doorStatus.setText("Doors: OPEN")
            else:
                self.doorStatus.setText("Doors: CLOSED")

            if(self.isRoofOpen):
                self.roofStatus.setText("Roof: OPEN")
            else:
                self.roofStatus.setText("Roof: CLOSED")

            if(self.isPadExtended):
                self.backPadStatus.setText("Back Pad: EXTENDED")
            else:
                self.backPadStatus.setText("Back Pad: RETRACTED")

            if(self.isPadRaised):
                self.roofPadStatus.setText("Top Pad: RAISED")
            else:
                self.roofPadStatus.setText("Top Pad: LOWERED")
            
            # Top Buttons
            if(self.isOn):
                self.systemStatus.setText("System Power: ON")
                self.emergencyStop.setDisabled(False)
                self.passwordoverride.setDisabled(False)
            else:
                self.systemStatus.setText("System Power: OFF")
                self.emergencyStop.setDisabled(True)
                self.passwordoverride.setDisabled(True)

            # Doors
            if(self.isOn and not self.isDoorOpen):
                self.openDoors.setDisabled(False)
            else: 
                self.openDoors.setDisabled(True)

            if(self.isOn and self.isDoorOpen and not self.isPadExtended):
                self.closeDoors.setDisabled(False)
            else: 
                self.closeDoors.setDisabled(True)

            # Roof
            if(self.isOn and not self.isRoofOpen):
                self.openRoof.setDisabled(False)
            else: 
                self.openRoof.setDisabled(True)

            if(self.isOn and self.isRoofOpen and not self.isPadRaised):
                self.closeRoof.setDisabled(False)
            else: 
                self.closeRoof.setDisabled(True)

            # Pad Extend
            if(self.isOn and self.isDoorOpen and not self.isPadExtended):
                self.extendPad.setDisabled(False)
            else: 
                self.extendPad.setDisabled(True)

            if(self.isOn and self.isPadExtended):
                self.retractPad.setDisabled(False)
            else: 
                self.retractPad.setDisabled(True)

            # Pad Raise
            if(self.isOn and self.isRoofOpen and not self.isPadRaised):
                self.raisePad.setDisabled(False)
            else: 
                self.raisePad.setDisabled(True)

            if(self.isOn and self.isPadRaised):
                self.lowerPad.setDisabled(False)
            else: 
                self.lowerPad.setDisabled(True)
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
                self.label.setText(str(e))
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
                self.label.setText("Invalid IP")
                self.submitConnect.setDisabled(False)
    
    # sendData: sends data to server
    def sendData(self, data):
        self.commandSock.sendall(data.encode())
        data = self.commandSock.recv(BUFFER_SIZE)
        data = data.decode()

        if "Error" in data:
                print("uh oh error!")
                self.systemDiagnostic()

        return data

    ######### Button Listeners #########
    def SystemPower(self):
        if self.isConnected:
            self.messagetext = self.sendData("systemPower")
            self.systemStatus.setText(self.messagetext)
            if self.messagetext == "System Power: ON":
                self.emergencyStop.setDisabled(False)
                self.passwordoverride.setDisabled(False)
                self.openDoors.setDisabled(False)
                self.openRoof.setDisabled(False)
            else:
                self.emergencyStop.setDisabled(True)
                self.passwordoverride.setDisabled(True)
                self.openDoors.setDisabled(True)
                self.openRoof.setDisabled(True)
                self.extendPad.setDisabled(True)
                self.raisePad.setDisabled(True)
        else:
            self.label.setText("Please Connect First")

    def EmergencyStop(self):
        if self.isConnected:
            self.messagetext = self.sendData("emergencyStop")
            self.systemStatus.setText(self.messagetext)
            self.emergencyStop.setDisabled(True)
            self.openDoors.setDisabled(True)
            self.closeDoors.setDisabled(True)
            self.openRoof.setDisabled(True)
            self.closeRoof.setDisabled(True)
            self.extendPad.setDisabled(True)
            self.retractPad.setDisabled(True)
            self.raisePad.setDisabled(True)
            self.lowerPad.setDisabled(True)
        else:
            self.label.setText("Please Connect First")

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
            self.doorStatus.setText(self.messagetext)
            self.openDoors.setDisabled(True)
            self.closeDoors.setDisabled(False)
            self.extendPad.setDisabled(False)
        else:
            self.label.setText("Please Connect First")

    def CloseDoors(self):
        if self.isConnected:
            self.messagetext = self.sendData("closeDoors")
            self.doorStatus.setText(self.messagetext)
            self.closeDoors.setDisabled(True)
            self.openDoors.setDisabled(False)
            self.extendPad.setDisabled(True)
        else:
            self.label.setText("Please Connect First")

    def OpenRoof(self):
        if self.isConnected:
            self.messagetext = self.sendData("openRoof")
            self.roofStatus.setText(self.messagetext)
            self.openRoof.setDisabled(True)
            self.closeRoof.setDisabled(False)
            self.raisePad.setDisabled(False)
        else:
            self.label.setText("Please Connect First")

    def CloseRoof(self):
        if self.isConnected:
            self.messagetext = self.sendData("closeRoof")
            self.roofStatus.setText(self.messagetext)
            self.closeRoof.setDisabled(True)
            self.openRoof.setDisabled(False)
            self.raisePad.setDisabled(True)
        else:
            self.label.setText("Please Connect First")

    def ExtendPad(self):
        if self.isConnected:
            self.messagetext = self.sendData("extendPad")
            self.backPadStatus.setText(self.messagetext)
            self.extendPad.setDisabled(True)
            self.retractPad.setDisabled(False)
            self.closeDoors.setDisabled(True)
        else:
            self.label.setText("Please Connect First")

    def RetractPad(self):
        if self.isConnected:
            self.messagetext = self.sendData("retractPad")
            self.backPadStatus.setText(self.messagetext)
            self.retractPad.setDisabled(True)
            self.extendPad.setDisabled(False)
            self.closeDoors.setDisabled(False)
        else:
            self.label.setText("Please Connect First")

    def RaisePad(self):
        if self.isConnected:
            self.messagetext = self.sendData("raisePad")
            self.roofPadStatus.setText(self.messagetext)
            self.raisePad.setDisabled(True)
            self.lowerPad.setDisabled(False)
            self.closeRoof.setDisabled(True)
        else:
            self.label.setText("Please Connect First")

    def LowerPad(self):
        if self.isConnected:
            self.messagetext = self.sendData("lowerPad")
            self.roofPadStatus.setText(self.messagetext)
            self.lowerPad.setDisabled(True)
            self.raisePad.setDisabled(False)
            self.closeRoof.setDisabled(False)
        else:
            self.label.setText("Please Connect First")

######### Running client #########
if __name__ == '__main__':
    app = Flask(__name__)
    client =  Form()
    client.init_gui(app, width=800, height=800, window_title="Nest Client", argv=None)
