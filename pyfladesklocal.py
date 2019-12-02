import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket
import server
import threading

s = server.Server()
serverThread = threading.Thread(target=s.connection)
serverThread.daemon = True
serverThread.start()
cur_host = s.UDP_IP_ADDRESS


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


def init_gui(application, port=0, width=800,    height=600, window_title="PyFladesk",      icon="appicon.png", argv=None):
    if argv is None:
        argv = sys.argv

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()
    
    print(" * Listening to commands on: " + s.UDP_IP_ADDRESS)
    print(s.getSystemStatusDict())

    # Application Level
    qtapp = QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Main Window Level
    window = QWidget()
    window.resize(width, height)
    window.setWindowTitle(window_title)
    window.setWindowIcon(QtGui.QIcon(icon))

    # WebView Level
    layout = QVBoxLayout()
    gridLayout = QGridLayout()
    vidLayout = QHBoxLayout()
    
    webView = QtWebEngineWidgets.QWebEngineView(window)
    webView.setMinimumHeight(520)
    vidLayout.addWidget(webView)

    
    gridLayout.addWidget(QLabel("System on: " + str(s.isOn)), 0, 0)
    gridLayout.addWidget(QLabel("Door open: " + str(s.isDoorOpen)), 1, 0)
    gridLayout.addWidget(QLabel("Roof open: " + str(s.isRoofOpen)), 2, 0)
    gridLayout.addWidget(QLabel("Pad extended: " + str(s.isPadExtended)), 3, 0)
    gridLayout.addWidget(QLabel("Pad raised: " + str(s.isPadRaised)), 4, 0)
    gridLayout.addWidget(QLabel("Stopped: " + str(s.isStopped)), 5, 0)
    
    layout.addLayout(vidLayout)
    layout.addLayout(gridLayout)
    
    window.setLayout(layout)

    # WebPage Level
    page = WebPage('http://' + cur_host + ':{}'.format(port))
    page.home()
    webView.setPage(page)

    window.show()
    return qtapp.exec_()
