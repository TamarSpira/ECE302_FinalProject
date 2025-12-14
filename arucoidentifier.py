from picamera2 import Picamera2
import cv2


# Initialize Pi camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# ArUco dictionaries to scan
aruco_dicts = {
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
}

print("Press Ctrl+C to stop")

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    for name, dictionary_id in aruco_dicts.items():
        dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)

        if ids is not None:
            print(f"Detected {name}, ID = {ids.flatten()[0]}")

    cv2.imshow("ArUco Detector", frame)
    if cv2.waitKey(1) & 0xFF == 27:   # ESC key
        break

cv2.destroyAllWindows()
picam2.stop()