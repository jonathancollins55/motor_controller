import lgpio
# import RPi.GPIO as gpio
import time

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 10
MIN_SIGNAL = 5
STEP_SIZE = .5

# gpio.setmode(gpio.BOARD)
# gpio.setup(MOTOR, gpio.OUT)
h = lgpio.gpiochip_open(0)

def main():
    #calibrate()
    arm()

    time.sleep(5)

    testMotorMovement()

    #accelerate()

    lgpio.gpiochip_close(h)

def accelerate():
    for i in range(MIN_SIGNAL,MAX_SIGNAL):
        lgpio.tx_pwm(h, MOTOR, FREQ, i/2)
        print("Signal is", i,"out of 20")
        time.sleep(1)

def manualMove():
    for i in range(10000):
        lgpio.gpio_write(h, MOTOR, 1)
        time.sleep(.002)
        lgpio.gpio_write(h, MOTOR, 0)
        time.sleep(.018)

def testMotorMovement():
    print("Frequency 1")
    lgpio.tx_pwm(h, MOTOR, FREQ, 10)    #May need to put this on a separate thread.
    time.sleep(8)

    # print("Frequency 2")
    # lgpio.tx_pwm(h, MOTOR, FREQ, 9)
    # time.sleep(3)

    # print("Frequency 3")
    # lgpio.tx_pwm(h, MOTOR, FREQ, 5)
    # time.sleep(3)

def spinToWin():
    lgpio.tx_pwm(h, MOTOR, FREQ, 10)
    time.sleep(10)

def calibrate():
    turn_off_power = input("Disconnect Power then press any key...")

    print("Now calibrating ESC")
    print("Now writing maximum output...")

    lgpio.tx_pwm(h, MOTOR, FREQ, MAX_SIGNAL)
    turn_on_power = input("Turn on power source, then wait 2 seconds and press any key")


    print("Sending minimum output")
    lgpio.tx_pwm(h, MOTOR, FREQ, MIN_SIGNAL)

    time.sleep(7)
    print("Wait for it...")
    time.sleep(5)

    lgpio.tx_pwm(h, MOTOR, FREQ, 0)
    time.sleep(2)
    print("Arming ESC now...")

    lgpio.tx_pwm(h, MOTOR, FREQ, MIN_SIGNAL)

    time.sleep(1)

    print("Finished Arming")

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
    #testMotorMovement()
    #spinToWin()
    #accelerate()