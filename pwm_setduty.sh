#!/bin/bash

NODE=/sys/class/pwm/pwmchip0
CHANNEL="$1"
PERIOD="$2"
DUTY_CYCLE="$3"

echo "$PERIOD" | sudo tee -a "$NODE/pwm$CHANNEL/period" > /dev/null
echo "$DUTY_CYCLE" | sudo tee -a "$NODE/pwm$CHANNEL/duty_cycle" > /dev/null
echo "1" | sudo tee -a "$NODE/pwm$CHANNEL/enable" > /dev/null
