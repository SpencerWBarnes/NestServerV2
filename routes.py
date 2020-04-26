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


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

machine = MachineStatus()

# home page
@app.route('/')
def index():
    return render_template('index.html')

def handleAuth():
    # TODO: Handle passwords
    auth = request.headers.get('auth')
    print("auth: " + str(auth))

# video stream generator function
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# video streaming routes

# route name is used for android app to access stream
@app.route('/video_feed1')
# function name is used as src for img tag in templates/index.html
def videoFeed1():
    # Camera param determines which camera
    return Response(gen(Camera(0)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def videoFeed2():
    return Response(gen(Camera(1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed3')
def videoFeed3():
    return Response(gen(Camera(2)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed4')
def videoFeed4():
    return Response(gen(Camera(3)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed5')
def videoFeed5():
    return Response(gen(Camera(4)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed6')
def videoFeed6():
    return Response(gen(Camera(5)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# drone landing image routes

# route named similarly for app video switching
@app.route('/video_feed7')
def topLandingImage():
    return Response(gen(Top_Landing_Camera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed8')
def bottomLandingImage():
    return Response(gen(Bottom_Landing_Camera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')


# command routes
@app.route('/systemPower')
def systemPower():
    message = machine.systemPower()
    return Response(message, mimetype='text')

@app.route('/emergencyStop')
def emergencyStop():
    message = machine.emergencyStop()
    return Response(message, mimetype='text')

@app.route('/openDoors')
def openDoors():
    handleAuth()
    message = machine.openDoors()
    return Response(message, mimetype='text')

@app.route('/closeDoors')
def closeDoors():
    handleAuth()
    message = machine.closeDoors()
    return Response(message, mimetype='text')

@app.route('/openRoof')
def openRoof():
    handleAuth()
    message = machine.openRoof()
    return Response(message, mimetype='text')

@app.route('/closeRoof')
def closeRoof():
    handleAuth()
    message = machine.closeRoof()
    return Response(message, mimetype='text')

@app.route('/extendPad')
def extendPad():
    handleAuth()
    message = machine.extendPad()
    return Response(message, mimetype='text')

@app.route('/retractPad')
def retractPad():
    handleAuth()
    message = machine.retractPad()
    return Response(message, mimetype='text')

@app.route('/raisePad')
def raisePad():
    handleAuth()
    message = machine.raisePad()
    return Response(message, mimetype='text')

@app.route('/lowerPad')
def lowerPad():
    handleAuth()
    message = machine.lowerPad()
    return Response(message, mimetype='text')

@app.route('/systemStatus')
def systemStatus():
    handleAuth()
    message = machine.systemStatus()
    return Response(message, mimetype='application/json')

@app.route('/bottomDroneMission')
def bottomDroneMission():
    handleAuth()
    machine.startThread(lambda: machine.bottomDroneMission())
    message = 'bottomDroneMission'
    return Response(message, mimetype='text')

@app.route('/topDroneMission')
def topDroneMission():
    handleAuth()
    machine.startThread(lambda: machine.topDroneMission())
    message = 'topDroneMission'
    return Response(message, mimetype='text')

@app.route('/sendTestMessage')
def sendTestMessage():
    handleAuth()
    message = "Connection is good. Message recieved" 
    return Response(message, mimetype='text')
