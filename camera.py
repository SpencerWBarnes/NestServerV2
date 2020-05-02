import time
import threading
import cv2
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """event-like class that signals all active clients when a new frame is
    available"""
    
    def __init__(self):
        self.events = {}

    def wait(self):
        """invoked from each client's thread to wait for the next frame"""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """invoked by the camera thread when new frame is available"""
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
        """invoked from each client's thread after a frame was processed"""
        self.events[get_ident()][0].clear()



class Camera():
    # background thread that reads frames from camera
    thread = None
    # current frame is stored here by background thread
    frame = None
    # time of last client access to the camera  
    last_access = 0  
    event = CameraEvent()

    def __init__(self, vsrc):
        # set video source
        self.video_source = vsrc

        # start background frame thread if not running
        if self.thread is None:
            self.last_access = time.time()

            # start background frame thread
            self.thread = threading.Thread(target=self._thread)
            self.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)
    
    def set_video_source(self, source):
        self.video_source = source

    def get_frame(self):
        """return current camera frame"""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        self.event.wait()
        self.event.clear()

        return self.frame

    def frames(self):
        camera = cv2.VideoCapture(self.video_source)
        if camera is None or not camera.isOpened():
            print('Camera  ' + str(self.video_source + 1) + ' not connected.')
            imgs = [(open('images/NoCamera.jpg', 'rb').read()), (open('images/BottomLanding.jpg', 'rb').read())]
            yield imgs[int(time.time()) % 2]

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            imgs = [(open('images/NoCamera.jpg', 'rb').read()), (open('images/BottomLanding.jpg', 'rb').read())]
            yield imgs[int(time.time()) % 2]

    def _thread( self):
        """camera background thread"""
        print('Starting camera ' + str(self.video_source + 1))
        frames_iterator = self.frames()
        for frame in frames_iterator:
            self.frame = frame
            self.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            # if time.time() - self.last_access > 10:
            #     frames_iterator.close()
            #     print('Stopping camera thread due to inactivity')
            #     break
        self.thread = None


class Top_Landing_Camera(Camera):
    @staticmethod
    def frames():
        while True:
            imgs = [(open('images/NoCamera.jpg', 'rb').read()), (open('images/BottomLanding.jpg', 'rb').read())]
            yield imgs[int(time.time()) % 2]

class Bottom_Landing_Camera(Camera):
    @staticmethod
    def frames():
        while True:
            imgs = [(open('images/NoCamera.jpg', 'rb').read()), (open('images/BottomLanding.jpg', 'rb').read())]
            yield imgs[int(time.time()) % 2]

