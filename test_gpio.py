# Test gpio pins for rasperry pi

import lgpio as LGPIO
from gpiozero import Servo
import time

# h = LGPIO.gpiochip_open(0)
# LGPIO.gpio_claim_output(h, 18)
# LGPIO.gpio_claim_output(h, 13)
# LGPIO.gpio_claim_output(h, 19)

# Tilt up/down:
# Min pulse makes it look flat ahead
# Middle pulse makes it look almost straight down
# Max pulse turns upside down (would break gun)

# Pan side/side

panServo = Servo(19, min_pulse_width=0.0005, max_pulse_width=0.0025)
tiltServo = Servo(13, min_pulse_width=0.0005, max_pulse_width=0.0025)
# LGPIO.setmode(GPIO.BCM)
# LGPIO.setup(18, GPIO.OUT)

while True:
    # LGPIO.gpio_write(h, 18, 1)
    # LGPIO.gpio_write(h, 13, 1)

    # time.sleep(0.5)
    # LGPIO.gpio_write(h, 13, 0)

    # time.sleep(0.5)
    # LGPIO.gpio_write(h, 18, 0)
    # time.sleep(1)

    print("Turning right:")
    tiltServo.value = -1
    panServo.value = -1

    time.sleep(1)

    print("Turning to middle:")
    tiltServo.value = -0.5
    panServo.value = 0

    time.sleep(1)

    print("Turning left:")
    tiltServo.value = 0
    panServo.value = 1

    time.sleep(1)