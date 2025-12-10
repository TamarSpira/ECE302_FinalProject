from picamera2 import Picamera2
import cv2
import numpy as np

# ---- CONFIGURE YOUR DICTIONARY HERE ----
# for example: cv2.aruco.DICT_6X6_100
ARUCO_DICT_ID = cv2.aruco.DICT_6X6_50
ARUCO_TARGET_ID = 3

dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID)
parameters = cv2.aruco.DetectorParameters()

# ---- Pi Camera setup ----
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (1280, 720)}
)
picam2.configure(config)
picam2.start()

print("Tracking Car... press Ctrl+C to exit.")

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    corners, ids, rejected = cv2.aruco.detectMarkers(
        gray, dictionary, parameters=parameters
    )

    if ids is None:
        print("where am I?")
        continue
    elif ARUCO_TARGET_ID in ids:
        car = int(np.where(ids == ARUCO_TARGET_ID)[0])
        tag_corners = corners[car]

        # Draw bounding box around tag(car)
        cv2.aruco.drawDetectedMarkers(frame, [tag_corners])

        # Optionally show center point too:
        pts = tag_corners[0]      # shape: (4,2)
        cx = int(pts[:,0].mean())
        cy = int(pts[:,1].mean())
        cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)

        print("Tag found at center:", cx, cy)
    else:
        tag_corners = None

    cv2.imshow("ArUco Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cv2.destroyAllWindows()
picam2.stop()
