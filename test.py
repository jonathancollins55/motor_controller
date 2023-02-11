import lgpio
# import RPi.GPIO as gpio
import time

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 10
MIN_SIGNAL = 3.5
STEP_SIZE = .5

# gpio.setmode(gpio.BOARD)
# gpio.setup(MOTOR, gpio.OUT)
h = lgpio.gpiochip_open(0)

def main():
    arm()

    time.sleep(5)

    testMotorMovement()

    accelerate()

    lgpio.gpiochip_close(h)

# def calibrate():
    
#     return

def accelerate():
    for i in range(MIN_SIGNAL,MAX_SIGNAL,STEP_SIZE):
        lgpio.tx_pwm(h, MOTOR, FREQ, i)
        time.sleep(1)

def testMotorMovement():
    print("Frequency 1")
    lgpio.tx_pwm(h, MOTOR, FREQ, 10)
    time.sleep(3)

    print("Frequency 2")
    lgpio.tx_pwm(h, MOTOR, FREQ, 10)
    time.sleep(3)

    print("Frequency 3")
    lgpio.tx_pwm(h, MOTOR, FREQ, 5)
    time.sleep(3)

def arm():
    turn_off_power = input("Disconnect Power then press any key...")

    print("Now calibrating ESC")
    print("Now writing maximum output...")

    lgpio.tx_pwm(h, MOTOR, FREQ, MAX_SIGNAL)
    turn_on_power = input("Turn on power source, then wait 2 seconds and press any key")


    print("Sending minimum output")
    lgpio.tx_pwm(h, MOTOR, FREQ, MIN_SIGNAL)

    time.sleep(2)

    print("Finished Arming")

if __name__ == "__main__":
    main()