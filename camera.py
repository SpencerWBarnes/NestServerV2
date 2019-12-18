import numpy as np
import threading
import time
import cv2
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()



class BaseCamera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - BaseCamera.last_access > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        BaseCamera.thread = None



class Camera1(BaseCamera):
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera1.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera1.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()



class Camera2(BaseCamera):
    video_source = 1

    @staticmethod
    def set_video_source(source):
        Camera2.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera2.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()


class Camera3(BaseCamera):
    video_source = 2

    @staticmethod
    def set_video_source(source):
        Camera3.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera3.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()



class Camera4(BaseCamera):
    video_source = 3

    @staticmethod
    def set_video_source(source):
        Camera4.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera4.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()


class Camera5(BaseCamera):
    video_source = 4

    @staticmethod
    def set_video_source(source):
        Camera5.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera5.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()



class Camera6(BaseCamera):
    video_source = 5

    @staticmethod
    def set_video_source(source):
        Camera6.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera6.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

class Camera(BaseCamera):
    video_source1 = 0
    video_source2 = 1
    video_source3 = 2
    video_source4 = 3
    video_source5 = 4
    video_source6 = 5

    @staticmethod
    def set_video_source(sources):
        Camera.video_source1 = sources[0]
        Camera.video_source2 = sources[0]
        Camera.video_source3 = sources[0]
        Camera.video_source4 = sources[0]
        Camera.video_source5 = sources[0]
        Camera.video_source6 = sources[0]

    @staticmethod
    def frames():
        camera1 = cv2.VideoCapture(Camera.video_source1)
        camera2 = cv2.VideoCapture(Camera.video_source2)
        camera3 = cv2.VideoCapture(Camera.video_source3)
        camera4 = cv2.VideoCapture(Camera.video_source4)
        camera5 = cv2.VideoCapture(Camera.video_source5)
        camera6 = cv2.VideoCapture(Camera.video_source6)
        if not (camera1.isOpened() or camera2.isOpened() or camera3.isOpened() 
        or camera4.isOpened() or camera5.isOpened() or camera6.isOpened()):
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img1 = camera1.read()
            _, img2 = camera2.read()
            _, img3 = camera3.read()
            _, img4 = camera4.read()
            _, img5 = camera5.read()
            _, img6 = camera6.read()
            img1 = cv2.resize(img1, (704, 396))
            img2 = cv2.resize(img2, (704, 396))
            img3 = cv2.resize(img3, (704, 396))
            img4 = cv2.resize(img4, (704, 396))
            img5 = cv2.resize(img5, (704, 396))
            img6 = cv2.resize(img6, (704, 396))
            img = np.hstack((img1, img2, img3, img4, img5, img6))

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
