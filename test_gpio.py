# Test gpio pins for rasperry pi

import lgpio as LGPIO
import time

h = LGPIO.gpiochip_open(0)
LGPIO.gpio_claim_output(h, 18)
LGPIO.gpio_claim_output(h, 13)
LGPIO.gpio_claim_output(h, 19)



# LGPIO.setmode(GPIO.BCM)
# LGPIO.setup(18, GPIO.OUT)

while True:
    LGPIO.gpio_write(h, 18, 1)
    LGPIO.gpio_write(h, 13, 1)

    time.sleep(0.5)
    LGPIO.gpio_write(h, 13, 0)

    time.sleep(0.5)
    LGPIO.gpio_write(h, 18, 0)
    time.sleep(1)