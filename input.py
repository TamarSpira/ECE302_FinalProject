from gpiozero import DigitalInputDevice
from time import sleep
red_light = DigitalInputDevice(17, pull_up=False)
while True:
    print("Red light ON" if red_light.is_active else "Red light OFF")
    sleep(0.5)