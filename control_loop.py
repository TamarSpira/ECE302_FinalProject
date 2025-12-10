import cv2
import time
from picamera2 import Picamera2
import numpy as np
import subprocess
from gpiozero import DigitalInputDevice
from gpiozero import DigitalOutputDevice

def HW_GPIO_adjust_pantilt(error_x, error_y):
    global current_y_width
    global current_x_width
    global prev_error_y
    global prev_error_x
    global accum_y
    global accum_x

    diff_x = prev_error_x - error_x
    diff_y = prev_error_y - error_y

    print("Diff x:", diff_x)

    prev_error_y = error_y
    prev_error_x = error_x

    accum_y += error_y
    accum_x += error_x

    new_y_width = current_y_width + (KPy * error_y) + (KIy * accum_y) + (KDy * diff_y)
    new_x_width = current_x_width + (KPx * error_x) + (KIx * accum_x) + (KDx * diff_x)

    if new_y_width < MIN_WIDTH_NS: new_y_width = MIN_WIDTH_NS
    if new_y_width > MAX_WIDTH_NS: new_y_width = MAX_WIDTH_NS

    if new_x_width < MIN_WIDTH_NS: new_x_width = MIN_WIDTH_NS
    if new_x_width > MAX_WIDTH_NS: new_x_width = MAX_WIDTH_NS

    print("New y width: ", new_y_width)
    print("New x width", new_x_width)

    subprocess.run(["./pwm_script.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", f"{new_y_width}"], check=True, capture_output=True, text=True)
    subprocess.run(["./pwm_script.sh", f"{PAN_CHANNEL}", f"{PERIOD_NS}", f"{new_x_width}"], check=True, capture_output=True, text=True)

    current_y_width = new_y_width
    current_x_width = new_x_width

    return 0

#using camera motion detection
def is_moving(cx, cy, prev_cx, prev_cy, cam_dx, cam_dy):
    dx = prev_cx - cx
    dy = prev_cy - cy
    true_dx = dx - cam_dx
    true_dy = dy - cam_dy
    true_dist = np.sqrt(true_dx**2 + true_dy**2)
    if true_dist > 8:
        print("car is moving!")
        return True
    return False
   

MAX_WIDTH_NS = 2200000
MIN_WIDTH_NS = 600000
PERIOD_NS = 20000000
BUZZER_PERIOD = 1020408
BUZZER_DUTY_CYCLE = 510204

REDLIGHT_PIN = 17
LASER_POINTER_PIN = 16
TILT_CHANNEL = 0
PAN_CHANNEL = 1
TRIGGER_CHANNEL = 2
BUZZER_CHANNEL = 3

loop_count = 0

KPx = -700
KPy = 700
KIx = 0
KIy = 0
KDx = -50
KDy = 50

ARUCO_DICT_ID = cv2.aruco.DICT_6X6_50
ARUCO_TARGET_ID = 3

dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID)
parameters = cv2.aruco.DetectorParameters()

picam2 = Picamera2()
red_light = DigitalInputDevice(REDLIGHT_PIN, pull_up=False)
laser_pointer = DigitalOutputDevice(LASER_POINTER_PIN, initial_value=False)
print("turning laser on:")
laser_pointer.on()

middle_x = 320
middle_y = 240

current_y_width = 1700000
current_x_width = 1500000
prev_error_y = 0
prev_error_x = 0
accum_x = 0
accum_y = 0
prev_cx = 0
prev_cy = 0
motion = False



# initialize to neutral postition
print("Initializing to neutral position")
subprocess.run(["./pwm_script.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", f"{current_y_width}"], check=True, capture_output=True, text=True)
subprocess.run(["./pwm_script.sh", f"{PAN_CHANNEL}", f"{PERIOD_NS}", f"{current_x_width}"], check=True, capture_output=True, text=True)

try:
    config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
    )

    picam2.configure(config)
    picam2.start()
    laser_pointer.on() # test laser pointer
    time.sleep(2)
    # laser_pointer.off()
    init_frame = picam2.capture_array()
    prev_gray = init_frame
    bg_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=40, 
                                 qualityLevel=0.01, minDistance=10)

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        next_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, bg_pts, None)
        next_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, bg_pts, None)
        good_prev = bg_pts[status.flatten() == 1]
        good_next = next_pts[status.flatten() == 1]

        if good_prev is None or good_next is None or len(good_prev) == 0 or len(good_next) == 0:
            mean_shift = np.array([0, 0], dtype=float)
        else:
             mean_shift = (good_next - good_prev).mean(axis=0)
     


        
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, dictionary, parameters=parameters
        )

        if ids is None:
            print("where am I?")
        else:
            ids_flat = ids.flatten()
            #matches = np.where(ids_flat == ARUCO_TARGET_ID)[0]
            matches = ids_flat
            if matches.size > 0:
                # car_corners = corners[matches[0]]
                car_corners = corners[0]
                # Now you can draw or use these corners
                        # Draw bounding box around tag(car)
                cv2.aruco.drawDetectedMarkers(frame, [car_corners])

                pts = car_corners[0]      # shape: (4,2)
                cx = int(pts[:,0].mean())
                cy = int(pts[:,1].mean())
                cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)
                if prev_cx is not None and prev_cy is not None:
                    is_moving(cx, cy, prev_cx, prev_cy)
                else:
                    prev_cx = cx
                    prev_cy = cy

                print("Tag found at center:", cx, cy)
                error_y = middle_y - cy
                error_x = middle_x - cx
                HW_GPIO_adjust_pantilt(error_x, error_y)
            else:
                car_corners = None
                print("no matching tags :(")

        prev_gray = gray.copy()
        bg_pts = good_next.reshape(-1, 1, 2)
        prev_cx = cx
        prev_cy = cy
        cv2.imshow("ArUco Tracking", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break
except Exception as e:
        print(e)
finally:
    print("Exiting")
    picam2.stop()
    cv2.destroyAllWindows()


