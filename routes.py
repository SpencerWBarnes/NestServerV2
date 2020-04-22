#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from status import MachineStatus


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

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/topLanding')
def topLanding():
    return Response(gen(Top_Landing_Camera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/bottomLanding')
def bottomLanding():
    return Response(gen(Bottom_Landing_Camera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed1')
def video_feed1():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(0)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed2')
def video_feed2():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed3')
def video_feed3():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(2)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed4')
def video_feed4():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(3)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed5')
def video_feed5():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(4)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed6')
def video_feed6():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(5)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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
    message = machine.openDoors()
    return Response(message, mimetype='text')

@app.route('/closeDoors')
def closeDoors():
    message = machine.closeDoors()
    return Response(message, mimetype='text')

@app.route('/openRoof')
def openRoof():
    message = machine.openRoof()
    return Response(message, mimetype='text')

@app.route('/closeRoof')
def closeRoof():
    message = machine.closeRoof()
    return Response(message, mimetype='text')

@app.route('/extendPad')
def extendPad():
    message = machine.extendPad()
    return Response(message, mimetype='text')

@app.route('/retractPad')
def retractPad():
    message = machine.retractPad()
    return Response(message, mimetype='text')

@app.route('/raisePad')
def raisePad():
    message = machine.raisePad()
    return Response(message, mimetype='text')

@app.route('/lowerPad')
def lowerPad():
    message = machine.lowerPad()
    return Response(message, mimetype='text')

@app.route('/systemStatus')
def systemStatus():
    message = machine.systemStatus()
    return Response(message, mimetype='application/json')

@app.route('/bottomDroneMission')
def bottomDroneMission():
    machine.startThread(lambda: machine.bottomDroneMission())
    message = 'bottomDroneMission'
    return Response(message, mimetype='text')

@app.route('/topDroneMission')
def topDroneMission():
    machine.startThread(lambda: machine.topDroneMission())
    message = 'topDroneMission'
    return Response(message, mimetype='text')

@app.route('/sendTestMessage')
def sendTestMessage():
    message = "Connection is good. Message recieved" 
    return Response(message, mimetype='text')
