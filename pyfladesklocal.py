import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket
import server
import threading

######### Initializing the server thread #########
s = server.Server()
serverThread = threading.Thread(target=s.connection)
serverThread.daemon = True

# Start server connection
serverThread.start()

# Get the IP address from the server
cur_host = server.IP_ADDRESS


######### ApplicationThread: the thread for the webpage application #########
class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port
        self.host = cur_host

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, host=self.host, threaded=True)

######### WebPage: the web engine that displays webpage content #########
class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)

######### updateUI: this is a callback that updates the user interface when there are changes on the server #########
def updateUI(commandsLabel, ipLabel, isOnLabel, isDoorOpenLabel, isRoofOpenLabel, isPadExtendedLabel, isPadRaisedLabel):
    commandsLabel.setText("Last Command: " + str(s.messagetext))
    ipLabel.setText("IP: " + str(server.IP_ADDRESS))
    isOnLabel.setText("System on: " + str(s.isOn))
    isDoorOpenLabel.setText("Doors open: " + str(s.isDoorOpen))
    isRoofOpenLabel.setText("Roof open: " + str(s.isRoofOpen))
    isPadExtendedLabel.setText("Pad extended: " + str(s.isPadExtended))
    isPadRaisedLabel.setText("Pad raised: " + str(s.isPadRaised))

######### init_gui: initializes the user interface for this application and sets up constants #########
def init_gui(application, port=0, width=800, height=600, window_title="Nest", icon="appicon.png", argv=None):
    if argv is None:
        argv = sys.argv

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()

    print(" * Listening to commands on: " + server.IP_ADDRESS)
    print(s.getSystemStatusDict())

    # Application Level
    global qtapp
    qtapp = QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)
    qtapp.aboutToQuit.connect(s.closeEvent)

    # Main Window Level
    window = QWidget()
    window.resize(width, height)
    window.setWindowTitle(window_title)
    window.setWindowIcon(QtGui.QIcon(icon))

    # Layouts Level
    layout = QVBoxLayout()
    gridLayout = QGridLayout()
    statusLayout = QGridLayout()
    vidLayout = QHBoxLayout()

    # WebView Level
    webView = QtWebEngineWidgets.QWebEngineView(window)
    webView.setMinimumHeight(700)
    webView.setMinimumWidth(600)
    vidLayout.addWidget(webView)

    # Widgets Level
    commandsLabel = QLabel()
    commandsLabel.setAlignment(QtCore.Qt.AlignTop)

    ipLabel = QLabel()
    isOnLabel = QLabel()
    isDoorOpenLabel = QLabel()
    isRoofOpenLabel = QLabel()
    isPadExtendedLabel = QLabel()
    isPadRaisedLabel = QLabel()

    # Layouts - Setting layouts
    statusLayout.addWidget(ipLabel, 0, 0)
    statusLayout.addWidget(isOnLabel, 1, 0)
    statusLayout.addWidget(isDoorOpenLabel, 2, 0)
    statusLayout.addWidget(isRoofOpenLabel, 3, 0)
    statusLayout.addWidget(isPadExtendedLabel, 4, 0)
    statusLayout.addWidget(isPadRaisedLabel, 5, 0)

    gridLayout.addLayout(statusLayout, 0, 0)
    gridLayout.addWidget(commandsLabel, 0, 1)

    layout.addLayout(vidLayout)
    layout.addLayout(gridLayout)

    window.setLayout(layout)

    # WebPage Level
    page = WebPage('http://' + cur_host + ':{}'.format(port))
    page.home()
    webView.setPage(page)
    window.showMaximized()

    # Callbacks to update the UI upon server changes
    s.serverCallback = lambda: updateUI(commandsLabel, ipLabel, isOnLabel, isDoorOpenLabel, isRoofOpenLabel, isPadExtendedLabel, isPadRaisedLabel)
    updateUI(commandsLabel, ipLabel, isOnLabel, isDoorOpenLabel, isRoofOpenLabel, isPadExtendedLabel, isPadRaisedLabel)

    return qtapp.exec_()
