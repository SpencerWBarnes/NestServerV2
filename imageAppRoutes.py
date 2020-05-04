#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, request
from MachineStatus import MachineStatus


# import camera driver
'''
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera
'''
#
from camera import *


imageApp = Flask(__name__)
imageApp.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# home page
@imageApp.route('/')
def index():
    return render_template('imageApp.html')

# video stream generator function
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



# drone landing image routes

# route named similarly for app video switching
@imageApp.route('/video_feed7')
def topLandingImage():
    return Response(gen(Top_Landing_Camera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')

@imageApp.route('/video_feed8')
def bottomLandingImage():
    return Response(gen(Bottom_Landing_Camera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')