import lgpio
import time

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 10
MIN_SIGNAL = 5

def main():
    h = lgpio.gpiochip_open(0)
    arm(h)

def arm(self):
    print("Sending minimum output")
    lgpio.tx_pwm(self, MOTOR, FREQ, MIN_SIGNAL)
    turn_on_power = input("Turn on power source and press any key")
    time.sleep(3)

    print("Finished Arming")


if __name__ == "__main__":
    main()