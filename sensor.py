# Read 9-axis IMU values
# Uses Adafruit-Blinka, BNO055 libraries
# Author: Jonathan Jordan Collins

import sys
import time
import board
import busio
import adafruit_bno055
from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)
while True:
    #print("Quaternion: {}".format(sensor.quaternion))
    print("Rad/s: {}".format(sensor.gyro))
    time.sleep(1)

# i2c = I2C
# bno = BNO055.BNO055(i2c=i2c)

# bno.begin()