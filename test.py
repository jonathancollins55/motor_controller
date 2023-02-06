import lgpio
import time

MOTOR = 12
FREQ = 50

# gpio.setmode(gpio.BOARD)
# gpio.setup(MOTOR, gpio.OUT)
h = lgpio.gpiochip_open(0)


print("Frequency 1")
lgpio.tx_pwm(h, MOTOR, FREQ, 10)
time.sleep(2)

print("Frequency 2")
lgpio.tx_pwm(h, MOTOR, FREQ, 10)
time.sleep(2)

print("Frequency 3")
lgpio.tx_pwm(h, MOTOR, FREQ, 5)
time.sleep(2)

lgpio.gpiochip_close(h)

# try:
#     while True:
#         lgpio.tx_pwm(h, MOTOR, FREQ, 50)
#         time.sleep(10)

#         # lgpio.tx_pwm(h, MOTOR, FREQ, 100)
#         # time.sleep(10)

# except KeyboardInterrupt:
#     lgpio.tx_pwm(h, MOTOR, FREQ, 50)
#     lgpio.gpiochip_close(h)