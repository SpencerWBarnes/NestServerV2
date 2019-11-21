from importlib import import_module
import os
from flask import Flask
from pyfladesk import init_gui

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

app = Flask(__name__)

from routes import *

if __name__ == '__main__':
    init_gui(app)