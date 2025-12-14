from subprocess import Popen
from signal import pause
import os
import time
os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"
from gpiozero import Button, LED

for _ in range(10):
    try:
        led = LED(17)  # or your pin
        break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError("GPIO never became available")

button = Button(27)  # GPIO pin 17

def run_program():
    Popen(["python3", 
    "/home/tamar/Desktop/ECE302-FinalProj/ECE302_FinalProject/control_loop.py"])

button.when_pressed = run_program

print("Listening for button press...")
# button.wait_for_press()  # keeps script alive

pause()   