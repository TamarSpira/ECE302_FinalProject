import cv2
import time
from picamera2 import Picamera2
from gpiozero import Servo
import numpy as np


# Feedback control 
# Currently is very bad

def adjustPanTilt(error_x, error_y):
    adjust_x = 0
    adjust_y = tiltServo.value + (error_y / -480)

    if adjust_x > 1: adjust_x = 1
    if adjust_x < -1: adjust_x = -1
    if adjust_y > 0: adjust_y = 0
    if adjust_y < -1: adjust_y = -1


    panServo.value += 0
    tiltServo.value = adjust_y

    return 0


pi = Picamera2()

panServo = Servo(19, min_pulse_width=0.0005, max_pulse_width=0.0025)
tiltServo = Servo(13, min_pulse_width=0.0005, max_pulse_width=0.0025)

try:
    config = pi.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
    )

    pi.configure(config)
    pi.start()
    time.sleep(2)

    # Color range
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])

    # Height = 480
    # Width = 640

    middle_x = 320
    middle_y = 240

    # initialize to neutral postition
    tiltServo.value = 0.5

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
            print("Central pos: (%d, %d)" % (cx,cy))

            error_x = middle_x - cx
            error_y = middle_y - cy

            print("Error: (%d, %d)" % (error_x, error_y))
            adjustPanTilt(error_x, error_y)


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



