import time
import pigpio
import os

SERVO_PIN = 18           # Hardware-PWM-capable pin (12, 13, 18, or 19)
CENTER_PW = 1500         # Microseconds for center position
LEFT_PW = 500           # Microseconds for full left
RIGHT_PW = 2500          # Microseconds for full right

pi = pigpio.pi()         # Connect to local pigpio daemon

if not pi.connected:
    raise Exception("Could not connect to pigpio daemon")

pi.set_mode(SERVO_PIN, pigpio.OUTPUT)   # Set the pin as an output

while True:
    # Move to center position
    print("to middle...")
    pi.set_servo_pulsewidth(SERVO_PIN, CENTER_PW)
    time.sleep(1)

    # Move to left
    print("turning left...")
    pi.set_servo_pulsewidth(SERVO_PIN, LEFT_PW)
    time.sleep(1)

    # Move to right
    print("turning right...")
    pi.set_servo_pulsewidth(SERVO_PIN, RIGHT_PW)
    time.sleep(1)

    # Turn off the servo signal (stop sending pulses)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)

            # Press esc to exit
    if os.waitKey(33) == 27:
        break

print("Exiting")
pi.stop()
