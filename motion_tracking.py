from picamera2 import Picamera2
import subprocess
import time
import cv2
from gpiozero import DigitalInputDevice

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

car = None
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history = 200, varThreshold = 12, detectShadows= True)

try:
    config = pi.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
    )

    pi.configure(config)
    pi.start()
    time.sleep(2)
    print(current_y_width)
    while (True):
         
except Exception as e:
        print(e)
finally:
    print("Exiting")
    pi.stop()
