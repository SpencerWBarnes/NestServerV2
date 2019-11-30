from importlib import import_module
import os
import threading
import server
from flask import Flask
from pyfladesklocal import init_gui
from dotenv import load_dotenv
load_dotenv('.flaskenv')

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

app = Flask(__name__)

from routes import *

def startServer():
    s = server.Server()
    s.connection()

if __name__ == '__main__':
    serverThread = threading.Thread(target=startServer)
    serverThread.daemon = True
    serverThread.start()
    init_gui(app, port=8000, width=800, height=800, window_title="Nest Server", icon="appicon.png", argv=None)
    