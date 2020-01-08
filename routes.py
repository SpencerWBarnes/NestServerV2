#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

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


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed1')
def video_feed1():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera1()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed2')
def video_feed2():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera2()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed3')
def video_feed3():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera3()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed4')
def video_feed4():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera4()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed5')
def video_feed5():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera5()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed6')
def video_feed6():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera6()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')