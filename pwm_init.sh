#!/bin/bash

NODE=/sys/class/pwm/pwmchip0

echo "0" | sudo tee -a "$NODE/export" > /dev/null
echo "1" | sudo tee -a "$NODE/export" > /dev/null
echo "2" | sudo tee -a "$NODE/export" > /dev/null
echo "3" | sudo tee -a "$NODE/export" > /dev/null

# Sure, the pin is set to the correct alt mode by the dtoverlay at startup...
# But we'll do this to protect the user (me, the user is me) from themselves:
pinctrl set 12 a0
pinctrl set 13 a0
pinctrl set 18 a3
pinctrl set 19 a3

