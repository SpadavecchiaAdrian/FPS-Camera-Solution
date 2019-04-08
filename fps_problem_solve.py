# original de:
# ttps://github.com/waveform80/picamera/issues/327
import io
import time
from picamera import PiCamera
import cv2
import numpy
from threading import Thread
import time
import imutils
from imutils.video import FPS

w = 640
h = 480
fw = (w + 31) // 32 * 32
fh = (h + 15) // 16 * 16
Y = None
camera = PiCamera()
camera.resolution = (w, h)
camera.framerate = 40
camera.exposure_mode = 'off'
camera.awb_mode = 'off'
camera.awb_gains = 1
camera.shutter_speed = 15000
stream_done = False
cv2.namedWindow("detection", cv2.WINDOW_AUTOSIZE)


def diff(frame1, frame2):
    return int(cv2.sumElems(frame1)[0] - cv2.sumElems(frame2)[0])


def outputs():
    global Y
    stream = io.BytesIO()
    while not stream_done:

        yield stream

        stream.seek(0)
        Y = numpy.fromstring(stream.getvalue(), dtype=numpy.uint8, count=fw * fh).\
            reshape((fh, fw))

        stream.seek(0)
        stream.truncate()


def capt():
    # modifico capture_sequence
    camera.capture_sequence(outputs(), 'yuv', use_video_port=True)
    pass


def startcapt():
    t = Thread(target=capt, args=())
    t.daemon = True
    t.start()


# TEST
startcapt()
time.sleep(0.5)
diffs = []
frame2 = Y

fps = FPS().start()
while cv2.waitKey(1) != ord("q"):
    # cv2.imshow('detection',Y)
    frame1 = frame2
    time.sleep(0.020)
    diffs.append(diff(frame1, frame2))
    fps.update()

stream_done = True

fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
print(diffs)
cv2.destroyAllWindows()
camera.close()
