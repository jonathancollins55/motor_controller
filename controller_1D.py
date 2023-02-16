#In this file I need to build a black box controller for one axis, so that if I give it an angle to turn to, it will slew to that angle
from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import lgpio
import time

###################################
# Variables - Controller
###################################
kp = 1
ki = 1
kd = 1

###################################
# Other Variables
###################################
axis = 0                #Axis to slew on
target_position = 90    #relative target position (in degrees clockwise)
AXIS_REMAP_X = 0x00
AXIS_REMAP_Y = 0x01
AXIS_REMAP_Z = 0x02

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 10
MIN_SIGNAL = 5
STEP_SIZE = .5

########################################## 
# Main Function
# Inputs: None
# Outputs: None
##########################################
def main():
    current_position = 0

    motor, bno = setup()
    adjusted_target_position = get_target_position(bno=bno)

    while(True):
        try:
            current_position = get_position(bno=bno)
            print(get_error(adjusted_target_position,current_position))
            print("Adjusted target position:",adjusted_target_position)
            time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("Program terminated")
            stop_motor(motor)
            break

########################################## 
# Returns current position of sensor
# Inputs: BNO055 sensor
# Outputs: position on specified axis
##########################################
def get_position(bno):
    return bno.read_euler()[axis]

########################################## 
# Function to get angle of desired position
# Inputs: BNO055 sensor
# Outputs: absolute target position
##########################################
def get_target_position(bno):
    turn_degree = target_position % 360
    current_position = bno.read_euler()[axis]

    if(current_position + turn_degree > 360):
        return (current_position + turn_degree) % 360
    else:
        return current_position + turn_degree

########################################## 
# Returns error of sensor pointing for control algorithm
# Inputs: current position and target position
# Outputs: difference of target position and current position
##########################################
def get_error(target_position,current_position):
    return target_position-current_position

def setup():
    i2c = I2C
    bno = BNO055.BNO055(i2c=i2c)
    bno.begin()
    calibrate_sensor(bno=bno)
    

    h = lgpio.gpiochip_open(0)
    arm(h)

    return h, bno

########################################## 
# Stops the motor. Must be run at end of program
# Inputs: N/A
# Outputs: N/A
##########################################
def stop_motor(h):
    print("Stopping motor")
    lgpio.tx_pwm(h, MOTOR, FREQ, MIN_SIGNAL)
    time.sleep(10)
    lgpio.gpio_write(h, MOTOR, 0)
    lgpio.gpiochip_close(h)

########################################## 
# Arms the motor. Must be run before powering the motor
# Inputs: handle to gpio chip device (h)
# Outputs: N/A
##########################################
def arm(h):
    print("Sending minimum output")
    lgpio.tx_pwm(h, MOTOR, FREQ, MIN_SIGNAL)
    turn_on_power = input("Turn on power source and press any key")
    time.sleep(3)

    print("Finished Arming")

########################################## 
# Calibration function for BNO055 accelerometer, gyroscope and magnetometer.
# Requires user to move sensor to complete calibration
# Inputs: BNO055 sensor
# Outputs: None
##########################################
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



########################################## 
# Run Main function from command line
##########################################
if __name__ == "__main__":
    main()