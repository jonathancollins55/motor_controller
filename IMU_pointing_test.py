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

    file = open("calibration_data.txt",'rb')
    calibration_data = file.read(22)
    bno.set_calibration(calibration_data)
    file.close()
    print("Calibrated!")
    time.sleep(1)
    
    return bno

if __name__ == "__main__":
    main()