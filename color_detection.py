import cv2
import time
from picamera2 import Picamera2
import numpy as np
import subprocess
from gpiozero import DigitalInputDevice
from gpiozero import DigitalOutputDevice
# import csv



def HW_GPIO_adjust_pantilt(error_x, error_y):
    global current_y_width
    global current_x_width
    global prev_y_width
    global prev_x_width
    global accum_y
    global accum_x

    diff_x = current_x_width - prev_x_width
    diff_y = current_y_width - prev_y_width

    prev_y_width = current_y_width
    prev_x_width = current_x_width

    accum_y += error_y
    accum_x += error_x

    print("new y width: ", current_y_width + (KPy * error_y) + (KIy * accum_y) + (KDy * diff_y))
    print("new x width: ", current_x_width + (KPx * error_x) + (KIx * accum_x) + (KDx * diff_x))


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

MAX_WIDTH_NS = 2200000
MIN_WIDTH_NS = 600000
PERIOD_NS = 20000000


REDLIGHT_PIN = 17
LASER_POINTER_PIN = 16

TILT_CHANNEL = 0
PAN_CHANNEL = 1
TRIGGER_CHANNEL = 2
BUZZER_CHANNEL = 3

BUZZER_PERIOD = 1020408
BUZZER_DUTY_CYCLE = 510204

loop_count = 0

KPx = 0
KPy = 900

KIx = 0
KIy = 20

KDx = 0
KDy = 0

pi = Picamera2()
red_light = DigitalInputDevice(REDLIGHT_PIN, pull_up=False)
laser_pointer = DigitalOutputDevice(LASER_POINTER_PIN, initial_value=False)


# Color range
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Height = 480
# Width = 640

middle_x = 320
middle_y = 240

current_y_width = 1700000
current_x_width = 1500000
prev_y_width = 1700000
prev_x_width = 1500000


# initialize to neutral postition
subprocess.run(["./pwm_script.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", f"{current_y_width}"], check=True, capture_output=True, text=True)
subprocess.run(["./pwm_script.sh", f"{PAN_CHANNEL}", f"{PERIOD_NS}", f"{current_x_width}"], check=True, capture_output=True, text=True)

accum_x = 0
accum_y = 0

prev_area = None
size_error = 5 #need to revise (a lot)


try:
    config = pi.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
    )

    pi.configure(config)
    pi.start()
    laser_pointer.on() # test laser pointer
    time.sleep(2)
    # laser_pointer.off()

    print(current_y_width)

    while True:
        start_time = time.time()

        frame = pi.capture_array()
        frame = cv2.blur(frame, (3,3))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

        best_cntr = None
        max_area = 0
        for cntr in contours:
            area = cv2.contourArea(cntr)
            if area > max_area:
                max_area = area
                best_cntr = cntr
        
        if best_cntr is not None:
            M = cv2.moments(best_cntr)
            cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cv2.circle(frame,(cx,cy),10,(0, 0, 255),-1)
            # print("Central pos: (%d, %d)" % (cx,cy))

            error_x = middle_x - cx
            error_y = middle_y - cy

            print("Current Y PWM: ", current_y_width)
            print("Current X PWM: ", current_x_width)


            print("Error: (%d, %d)" % (error_x, error_y))
            # PIGPIOadjustPanTilt(error_x, error_y)
            HW_GPIO_adjust_pantilt(error_x, error_y)
            # if prev_area is not None: 
                # print("change in area = ", abs(area - prev_area))
                # with open('farfar.csv', 'a', newline='') as f:
                #     writer = csv.writer(f)
                #     writer.writerow([abs(area - prev_area)])
            if (prev_area is not None) and (abs(area - prev_area) > size_error) and red_light.is_active:
                # trigger buzzer
                subprocess.run(["./pwm_script.sh", f"{BUZZER_CHANNEL}", f"{BUZZER_PERIOD}", f'{BUZZER_DUTY_CYCLE}'], check=True, capture_output=True, text=True)
                # pull trigger
                print("motion detected on red light!")
                laser_pointer.on()
                time.sleep(1)

                # Turn buzzer and laser pointer off
                command = 'echo 0 | sudo tee /sys/class/pwm/pwmchip0/pwm3/enable'
                try:
                    # Use shell=True to run the full command string
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Command failed: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")
                laser_pointer.off()
            prev_area = area

        else:
            print("[Warning]Car lost...")                  
             

        # cv2.imshow("Captured frame", frame)
        # cv2.imshow("Mask", mask)

        loop_count += 1

        # # record end time
        # end_time = time.time()
        # # calculate FPS
        # seconds = end_time - start_time
        # fps = 1.0 / seconds
        # print("Estimated fps:{0:0.1f}".format(fps));

        # Press esc to exit
        if cv2.waitKey(33) == 27:
            break
except Exception as e:
        print(e)
finally:
    print("Exiting")
    pi.stop()
    cv2.destroyAllWindows()



