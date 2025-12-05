import cv2
import time
from picamera2 import Picamera2
import numpy as np
import subprocess


# Feedback control 
# Currently is very bad

# def adjustPanTilt(error_x, error_y):
#     global current_y_duty
#     adjust_x = 0
#     # adjust_y = tiltServo.value + (error_y / -480)
#     new_y_duty = current_y_duty + (error_y / -480)

#     # if adjust_x > 1: adjust_x = 1
#     # if adjust_x < -1: adjust_x = -1
#     # if adjust_y > 0: adjust_y = 0,,,,
#     # if adjust_y < -1: adjust_y = -1

#     if new_y_duty < MIN_DUTY_CYCLE: new_y_duty = MIN_DUTY_CYCLE
#     if new_y_duty > MAX_DUTY_CYLE: new_y_duty = MAX_DUTY_CYLE

#     current_y_duty = new_y_duty


#     # panServo.value += 0
#     # tiltServo.value = adjust_y
#     # tilt_pwm.ChangeDutyCycle(new_y_duty)

#     return 0


# def PIGPIOadjustPanTilt(error_x, error_y):
#     adjust_x = 0
#     # adjust_y = tiltServo.value + (error_y / -480)
#     new_y_width = servos.get_servo_pulsewidth(TILT_PIN) + (error_y / -480)

#     # if adjust_x > 1: adjust_x = 1
#     # if adjust_x < -1: adjust_x = -1
#     # if adjust_y > 0: adjust_y = 0,,,,
#     # if adjust_y < -1: adjust_y = -1

#     if new_y_width < MIN_WIDTH: new_y_width = MIN_WIDTH
#     if new_y_width > MAX_WIDTH: new_y_width = MAX_WIDTH

#     servos.set_servo_pulsewidth(TILT_PIN, new_y_width)


#     # panServo.value += 0
#     # tiltServo.value = adjust_y
#     # tilt_pwm.ChangeDutyCycle(new_y_width)

#     return 0

def HW_GPIO_adjust_pantilt(error_x, error_y):
    global current_y_width
    new_y_width = current_y_width + (KP * error_y)

    if new_y_width < MIN_WIDTH_NS: new_y_width = MIN_WIDTH_NS
    if new_y_width > MAX_WIDTH_NS: new_y_width = MAX_WIDTH_NS

    subprocess.run(["/home/tamar/pwm_script.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", f"{new_y_width}"], check=True, capture_output=True, text=True)

    current_y_width = new_y_width
    return 0


pi = Picamera2()
# servos = pigpio.pi()     

# panServo = Servo(19, min_pulse_width=0.0005, max_pulse_width=0.0025)
# tiltServo = Servo(13, min_pulse_width=0.0005, max_pulse_width=0.0025)

# MAX_DUTY_CYLE = 12.5
# MIN_DUTY_CYCLE = 2.5
# MIN_WIDTH = 500
# MAX_WIDTH = 2500

MAX_WIDTH_NS = 2500000
MIN_WIDTH_NS = 500000
PERIOD_NS = 20000000

PAN_PIN = 19

TILT_CHANNEL = 0

KP = -500

# servos.set_mode(PAN_PIN, pigpio.OUTPUT)   # Set the pin as an output


# Color range
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Height = 480
# Width = 640

middle_x = 320
middle_y = 240

# initialize to neutral postition
# tiltServo.value = 0.5

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(13, GPIO.OUT)

#N tilt_pwm = GPIO.PWM(13, 50)  # 50 Hz servo
# tilt_pwm.start(7)          # 7.5% duty = center
subprocess.run(["/home/tamar/pwm_script.sh", f"{TILT_CHANNEL}", f"{PERIOD_NS}", "1500000"], check=True, capture_output=True, text=True)

current_y_width = 150000


try:
    config = pi.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
    )

    pi.configure(config)
    pi.start()
    time.sleep(2)

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

            print("Current PWM: ", current_y_width)

            print("Error: (%d, %d)" % (error_x, error_y))
            # PIGPIOadjustPanTilt(error_x, error_y)
            HW_GPIO_adjust_pantilt(error_x, error_y)


        else:
            print("[Warning]Car lost...")                  
             

        cv2.imshow("Captured frame", frame)
        cv2.imshow("Mask", mask)

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



