import cv2
import time
from picamera2 import Picamera2
import numpy as np

pi = Picamera2()

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


    while True:
        frame = pi.capture_array()
        frame = cv2.blur(frame, (3,3))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        cv2.imshow("Captured frame", frame)
        cv2.imshow("Mask", mask)

        # Press esc to exit
        if cv2.waitKey(33) == 27:
            break
except Exception as e:
        print(e)
finally:
    print("Exiting")
    pi.stop()
    cv2.destroyAllWindows()



