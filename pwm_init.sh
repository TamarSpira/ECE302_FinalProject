#!/bin/bash

NODE=/sys/class/pwm/pwmchip0

echo "0" | sudo tee -a "$NODE/export" > /dev/null
echo "1" | sudo tee -a "$NODE/export" > /dev/null
echo "2" | sudo tee -a "$NODE/export" > /dev/null
echo "3" | sudo tee -a "$NODE/export" > /dev/null

pinctrl set 12 a0
pinctrl set 13 a0
pinctrl set 18 a3
pinctrl set 19 a3

