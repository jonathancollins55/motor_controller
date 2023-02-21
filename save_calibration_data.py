from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import time

def calibrate_sensor(bno):
    print("Move the sensor around and place it in different configurations to calibrate!")
    print("Calibrating....")
    while(bno.get_calibration_status()[1] != 3):
        print("Calibrating Gyroscope (3 is fully calibrated) | Currently: ", bno.get_calibration_status()[1])
        time.sleep(1)
    while(bno.get_calibration_status()[2] != 3):
        print("Calibrating Accelerometer (3 is fully calibrated) | Currently: ", bno.get_calibration_status()[2])
        time.sleep(1)
    while(bno.get_calibration_status()[3] != 3):
        print("Calibrating Magnetometer (3 is fully calibrated) | Currently: ", bno.get_calibration_status()[3])
        time.sleep(1)

    print("-----------------FULLY CALIBRATED-----------------")

i2c = I2C
bno = BNO055.BNO055(i2c=i2c)
bno.begin()
calibrate_sensor(bno=bno)

calibration_data = bno.get_calibration()
calibration_byte_array = bytearray(calibration_data)

immutable_calibration_data = bytes(calibration_byte_array)

with open("calibration_data.txt", "wb") as binary_file:
    binary_file.write(immutable_calibration_data)