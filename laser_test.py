import RPi.GPIO as GPIO
import time


GPIO.output(22, 1)
time.sleep(10)
GPIO.output(22,0)