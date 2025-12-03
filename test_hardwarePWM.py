from RPi import GPIO
import time


MAX_DUTY_CYLE = 12.5
MIN_DUTY_CYCLE = 2.5

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.OUT)

pwm = GPIO.PWM(13, 50)  # 50 Hz servo
pwm.start(7)          # 7.5% duty = center

while True:
    pwm.ChangeDutyCycle(MIN_DUTY_CYCLE)   # left
    time.sleep(1)
    pwm.ChangeDutyCycle(MAX_DUTY_CYLE)  # right
    time.sleep(1)