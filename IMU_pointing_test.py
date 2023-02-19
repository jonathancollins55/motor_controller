from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import time

axis = 0                #Axis to slew on
target_position = 90    #relative target position (in degrees clockwise)
AXIS_REMAP_X = 0x00
AXIS_REMAP_Y = 0x01
AXIS_REMAP_Z = 0x02

def main():
    current_position = 0

    bno = setup()

    while(True):
        try:
            current_position = get_pointing_3D(bno=bno)
            print(current_position)
            time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("Program terminated")
            break

def get_pointing(bno):
    return bno.read_euler()[axis]

def get_pointing_3D(bno):
    return [bno.read_euler()[axis],bno.read_euler()[1],bno.read_euler()[2]]

def setup():
    i2c = I2C
    bno = BNO055.BNO055(i2c=i2c)
    bno.begin()
    calibrate_sensor(bno=bno)
    
    return bno

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

if __name__ == "__main__":
    main()