import cv2
import time
from picamera2 import Picamera2
import numpy as np
import subprocess
from gpiozero import DigitalInputDevice
from gpiozero import DigitalOutputDevice
import csv

def HW_GPIO_adjust_pantilt(error_x, error_y):    
    global current_y_width
    global current_x_width
    global prev_error_y
    global prev_error_x
    global accum_y
    global accum_x

    diff_x = prev_error_x - error_x
    diff_y = prev_error_y - error_y

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

    # print("New y width: ", new_y_width)
    # print("New x width", new_x_width)
    with open('Kdxvar/neg120/xErr.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([error_x])
    with open('Kdxvar/neg120/yErr.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([error_y])
    with open('Kdxvar/neg120/xDiff.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([diff_x])
    with open('Kdxvar/neg120/yDiff.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([diff_y])
     # start_pwm = time.time()

    subprocess.run(["./pwm_setduty.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", f"{new_y_width}"], shell=False, capture_output=True)
    subprocess.run(["./pwm_setduty.sh", f"{PAN_CHANNEL}", f"{PERIOD_NS}", f"{new_x_width}"], shell=False, capture_output=True)

    # end_pwm = time.time()
    # print(f"Bash latency: {end_pwm - start_pwm}")

    current_y_width = new_y_width
    current_x_width = new_x_width

    return 0

def is_moving_area(area, prev_area):
    global AREA_THRESH
    percent_change = abs(prev_area - area) / prev_area
    print("Percent change:", percent_change)

    if area < 300:
        AREA_THRESH = 0.08
    else:
        AREA_THRESH = 0.065

    if percent_change > AREA_THRESH:
        with open('Kdxvar/neg120/areanotifs.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([area, True])
        return True
    else: 
        with open('Kdxvar/neg120/areanotifs.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([area, False])
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

KPx = 0 # actual: -700
KPy =0 # actual: 700
KIx = 0
KIy = 0
KDx = -120 # actual: -100
KDy = 0 # actual: 100



AREA_THRESH = 0.05

ARUCO_DICT_ID = cv2.aruco.DICT_6X6_50
ARUCO_TARGET_ID = 3

dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID)
parameters = cv2.aruco.DetectorParameters()

picam2 = Picamera2()
red_light = DigitalInputDevice(REDLIGHT_PIN, pull_up=False)
laser_pointer = DigitalOutputDevice(LASER_POINTER_PIN, initial_value=False)
# for i in range(0,3): # flash 3 times to show code is running
#     laser_pointer.on()
#     time.sleep(0.5)
#     laser_pointer.off()

MIDDLE_X = 320
MIDDLE_Y = 240

current_y_width = 1100000
current_x_width = 1500000
prev_error_y = 0
prev_error_x = 0
accum_x = 0
accum_y = 0
prev_area = None
area = None



# Initialize HW pwm
subprocess.run(["./pwm_init.sh"], check=True, capture_output=True, text=True)


# initialize to neutral postition
print("Initializing to neutral position")
subprocess.run(["./pwm_setduty.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", f"{1100000}"], check=True, capture_output=True, text=True)
subprocess.run(["./pwm_setduty.sh", f"{PAN_CHANNEL}", f"{PERIOD_NS}", f"{current_x_width}"], check=True, capture_output=True, text=True)

try:
    config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
    )
    laser_pointer.on()

    picam2.configure(config)
    picam2.start()
    # laser_pointer.on()
    # time.sleep(2)
    # laser_pointer.off()

    while True:
        start = time.time()
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, dictionary, parameters=parameters)

        if ids is None:
            print("where am I?")
        else:
            ids_flat = ids.flatten()
            if ids_flat.size > 0:
                print("gotem")
                car_corners = corners[0]
                area = cv2.contourArea(car_corners)
                with open('Kdxvar/neg120/areah.csv', 'a', newline='') as f:
                     writer = csv.writer(f)
                     writer.writerow([area])
                # Now you can draw or use these corners
                        # Draw bounding box around tag(car)
                # cv2.aruco.drawDetectedMarkers(frame, [car_corners])

                pts = car_corners[0]      # shape: (4,2)
                cx = int(pts[:,0].mean())
                cy = int(pts[:,1].mean())
                # cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)
                if prev_area is not None:
                    if is_moving_area(area, prev_area) and red_light.is_active:
                        laser_pointer.on()
                        subprocess.run(["./pwm_setduty.sh", f"{BUZZER_CHANNEL}", f"{BUZZER_PERIOD}", f'{BUZZER_DUTY_CYCLE}'], check=True, capture_output=True, text=True)
                        time.sleep(0.1) # With the bad latency we have, this is akin to skipping ~1 frame. Should not affect control too much

                        # Turn buzzer and laser pointer off
                        # laser_pointer.off()
                        command = 'echo 0 | sudo tee /sys/class/pwm/pwmchip0/pwm3/enable'
                        try:
                            # Use shell=True to run the full command string
                            subprocess.run(command, shell=True, capture_output=True, check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Command failed: {e}")
                        except Exception as e:
                            print(f"An error occurred: {e}")

                else:
                    prev_area = area

                # print("Tag found at center:", cx, cy)
                error_y = MIDDLE_Y - cy
                error_x = MIDDLE_X - cx
                HW_GPIO_adjust_pantilt(error_x, error_y)
            else:
                car_corners = None
                print("no matching tags :(")

        prev_area = area
        cv2.imshow("ArUco Tracking", frame)

        end = time.time()
        latency = end - start
        print(f"Total latency: {latency}")
        print(f"FPS {1/latency}")
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break
except Exception as e:
        print(e)
finally:
    print("Exiting")
    picam2.stop()
    cv2.destroyAllWindows()


