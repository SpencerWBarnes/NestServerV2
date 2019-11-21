from flask import render_template, Response
from app import app
from importlib import import_module
import os

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')


"""video streaming generator function."""
def cam_gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


"""video streaming routes"""
@app.route('/video_feed1')
def video_feed1():
    
    return Response(cam_gen(Camera(0)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    return Response(cam_gen(Camera(1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')