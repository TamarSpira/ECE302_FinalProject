from picamera2 import Picamera2
import subprocess
import time
import cv2
from gpiozero import DigitalInputDevice
import numpy as np

MAX_WIDTH_NS = 2000000
MIN_WIDTH_NS = 700000
PERIOD_NS = 20000000


REDLIGHT_PIN = 17

TILT_CHANNEL = 0
PAN_CHANNEL = 1
TRIGGER_CHANNEL = 2
BUZZER_CHANNEL = 3

BUZZER_PERIOD = 1020408
BUZZER_DUTY_CYCLE = 510204


KP = -1000

pi = Picamera2()
red_light = DigitalInputDevice(REDLIGHT_PIN, pull_up=False)


# Color range
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Height = 480
# Width = 640

middle_x = 320
middle_y = 240

# initialize to neutral postition
subprocess.run(["./pwm_script.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", "1500000"], check=True, capture_output=True, text=True)
subprocess.run(["./pwm_script.sh", f"{PAN_CHANNEL}", f"{PERIOD_NS}", "1500000"], check=True, capture_output=True, text=True)


current_y_width = 150000
current_x_width = 150000

prev_area = None
size_error = 5 #need to revise (a lot)

tracking = False
bbox = None

bg_subtractor = cv2.createBackgroundSubtractorMOG2(history = 200, varThreshold = 12, detectShadows= True)

# use motion tracking to find car (with biggest contour filtered by size)
def detect_car_MOG2(frame):
    fgmask = bg_subtractor.apply(frame)
    # Threshold to remove shadows & noise
    _, motion_mask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

    blue_strength = frame[:,:,0] - frame[:,:,2]   # B - R
    _, blue_mask = cv2.threshold(blue_strength, 20, 255, cv2.THRESH_BINARY)

    mask = cv2.bitwise_and(motion_mask, blue_mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    
   #  contours = [c for c in contours if 300 < cv2.contourArea(c) < 20000]
    if not contours:
        return None

    # Pick the largest one as initial detection
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)

    return (x, y, w, h)

try:
    config = pi.create_video_configuration(
    main={"size": (640, 480), "format": "XBGR8888"}
    )

    pi.configure(config)
    pi.start()
    time.sleep(2)
    while (True):
        frame = pi.capture_array()
        display = frame.copy()
        frame = frame[:, :, :3]  # convert BGRA → BGR
        if tracking:
            ok, bbox = car.update(frame)
            if ok:
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
            else:
                tracking = False
                bbox = None
                cv2.putText(display, "Lost! Switching to detection...",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        else:
            bbox = detect_car_MOG2(frame)
            if bbox is not None:
                car = cv2.TrackerKCF_create()
                car.init(frame, tuple(bbox))
                tracking = True
                x, y, w, h = bbox
                cv2.rectangle(display, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(display, "Car detected — Tracker initialized",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("Tracking", display)
        if cv2.waitKey(33) == 27:
            break

         
except Exception as e:
        print(e)
finally:
    cv2.destroyAllWindows()
    print("Exiting")
    pi.stop()
