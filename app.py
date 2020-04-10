from importlib import import_module
import os
import threading
from flask import Flask
from pyfladesklocal import init_gui
from dotenv import load_dotenv
load_dotenv('.flaskenv')

# Setting up cameras
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Creating flask application
app = Flask(__name__)
from routes import * # This has to be here, it can't be moved up to the top

# Running applciation
if __name__ == '__main__':
    init_gui(app, port=8000, width=1400, height=600, window_title="Nest Server", icon="appicon.jpg", argv=None)
    