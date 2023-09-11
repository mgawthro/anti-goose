

import RPi.GPIO as GPIO
import time


'''
(pan, tilt)
laser home position (4.5, 8.5)

pan range 3.5-5.5
    5.5 is left
    3.5 is right
tilt range 8.5-10
    8.5 is straight
    10 is down
'''


'''
REQUIRES: 
    GPIOs are set to output
EFFECT:
    Zig Zag pattern to scare geese
'''
def zigzag(full, far):
    #assume servos are set to active
    if(full):
        add= 2/6
        duty = 8
    elif ~full and far:
        add = 1/6
        duty = 8.5
    elif(~full and ~far):
        add = 1/6
        duty = 9.25
    else:
        print("error: invalid zigzag input")
        return


    #start at furthest left
    tilt.ChangeDutyCycle(8.5)
    pan.ChangeDutyCycle(5.5)
    time.sleep(5)
    GPIO.output(22, 1) #laser on

    i = 0
    while(i < 6):
        GPIO.output(22, 1)
        if(i%2 == 0):
            pan.ChangeDutyCycle(3.5)
        else:
            pan.ChangeDutyCycle(5.5)
        duty = duty + add
        tilt.ChangeDutyCycle(duty)
        
        
        time.sleep(0.5)
        i = i +1
    GPIO.output(22, 0)


def circle():
    #start at top of circle
    pan.ChangeDutyCycle(4.5)
    tilt.ChangeDutyCycle(8.5)
    time.sleep(4)
    i = 0
    tilt_add = 1/6
    pan_add = 1/6
    pan_duty = 4.5
    tilt_duty = 8.5
    GPIO.output(22, 1)
    while i < 24:
        if i < 12:
            if(i <= 6):
                pan_duty = pan_duty - pan_add
                pan.ChangeDutyCycle(pan_duty)
            else:
                pan_duty = pan_duty + pan_add
                pan.ChangeDutyCycle(pan_duty)
            tilt_duty = tilt_duty + tilt_add
            tilt.ChangeDutyCycle(tilt_duty)
        else:
            if(i <= 18):
                pan_duty = pan_duty + pan_add
                pan.ChangeDutyCycle(pan_duty)
            else:
                pan_duty = pan_duty - pan_add
                pan.ChangeDutyCycle(pan_duty)
            tilt_duty = tilt_duty - tilt_add
            tilt.ChangeDutyCycle(tilt_duty)
        time.sleep(0.1)
        i = i + 1
    GPIO.output(22, 0)

GPIO.setmode(GPIO.BCM)

#activating GPIO pins
GPIO.setup(27, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)


tilt = GPIO.PWM(27, 50)  # PWM frequency is 50Hz
pan = GPIO.PWM(17,50)

tilt.start(8.5)  # Initialization
pan.start(4.5)

time.sleep(2)

circle()
zigzag(True, False)
zigzag(False, True)
zigzag(False, False)

'''
time.sleep(3)
#tilt.ChangeDutyCycle(10)  # Rotate the servo motor to 90 degrees
pan.ChangeDutyCycle(3.5)
GPIO.output(22, 1)
time.sleep(1)
#tilt.ChangeDutyCycle(6)  # Rotate the servo motor to 180 degrees
pan.ChangeDutyCycle(5.5)
GPIO.output(22, 0)
time.sleep(1)
'''
tilt.stop()
pan.stop()
GPIO.cleanup()

def angle(duty):
    return (duty-2)*18

def home():
    tilt.ChangeDutyCycle(8)
    pan.ChangeDutyCycle(4.5)
    time.sleep(0.5)

        

        

        