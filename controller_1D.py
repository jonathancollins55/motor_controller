#In this file I need to build a black box controller for one axis, so that if I give it an angle to turn to, it will slew to that angle
from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import lgpio
import time
import csv
import matplotlib.pyplot as plt

###################################
# Variables - Controller
###################################
kp = 1
ki = 1
kd = 1

prevT = 0
eprev = 0
eintegral = 0
pwm_prev = 5

###################################
# Other Variables
###################################
axis = 0                #Axis to slew on
target_position = -90    #relative target position (in degrees clockwise)
AXIS_REMAP_X = 0x00
AXIS_REMAP_Y = 0x01
AXIS_REMAP_Z = 0x02

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 10
MIN_SIGNAL = 5
STEP_SIZE = .2

########################################## 
# Main Function
# Inputs: None
# Outputs: None
##########################################
def main():
    ###################################
    # Variables - Controller
    ###################################
    kp = -1/90
    ki = 0
    kd = 0

    prevT = 0
    eprev = 0
    eintegral = 0
    pwm_prev = 5.3
    MAXIMUM_ERROR = 1.5

    ###################################
    # Other Variables
    ###################################
    axis = 0                #Axis to slew on
    #target_position = -10    #relative target position (in degrees clockwise) (Must be negative for unidirectional motor)
    AXIS_REMAP_X = 0x00
    AXIS_REMAP_Y = 0x01
    AXIS_REMAP_Z = 0x02

    MOTOR = 12
    FREQ = 50
    MAX_SIGNAL = 10
    MIN_SIGNAL = 5
    STEP_SIZE = .025

    current_position = 0

    motor, bno = setup()
    target_position = get_target_position(bno=bno)

    print("target position is:",target_position)
    time.sleep(2)
    print("Starting control")
    time.sleep(3)

    #FOR ERROR PLOTTING
    plot = [[],[]]      #Error
    io_data = [[],[],[]]   #FOR SYSTEM ANALYZER
    TIME_START = time.time()    

    while(True):
        prevT = 0
        try:
            #time difference
            currT = time.time_ns()
            deltaT = currT-prevT/1.0e9  #CHANGE 1nS TO TIME DELAY USED BELOW
            prevT = currT

            #error
            current_position = get_position(bno)
            e = target_position-current_position

            dedt = (e-eprev)/deltaT
            eintegral = eintegral + e*deltaT

            #Calculate control signal
            u = kp*e + kd*dedt + ki*eintegral
            pwm = MIN_SIGNAL + u

            #Plotting Error
            plot[0].append(time.time()-TIME_START)
            plot[1].append(e)

            #Plotting Input, Output
            io_data[0].append(time.time()-TIME_START)
            io_data[1].append(pwm)
            io_data[2].append(current_position)

            print("Error:",e,"Control_Signal:",pwm)
            #print("Gyroscope value", bno.read_gyroscope()[axis])
            set_motor(motor,pwm)    #Put in await function. Continuously monitor error and change PID vals, but slowly change PWM
            time.sleep(1)
            pwm_prev = pwm

        except KeyboardInterrupt:
            print()
            print("Terminating Program...")
            time.sleep(1)
            stop_motor(motor)

            # writing error data into file
            file = open('e_plot.csv', 'w+', newline ='')            
            with file:   
                write = csv.writer(file)
                write.writerows(plot)
                #write.writerows(map(lambda x: [x], e_plot))
            file.close()

            #Writing IO data into file
            file = open('io_data.csv', 'w+', newline='')
            with file:
                write = csv.writer(file)
                write.writerows(io_data)

            plt.plot(plot[0],plot[1])
            plt.xlabel("Time (in seconds)")
            plt.ylabel("Error (in degrees)")
            plt.savefig('error.png')

            plt.close()

            plt.plot(io_data[1],io_data[2])
            plt.xlabel("Input (duty cycle)")
            plt.ylabel("Position (in degrees)")
            plt.savefig('io.png')

            plt.close()

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

########################################## 
# Sets speed of motor as a pwm signal (5-10% duty cycle)
# Inputs: Motor instance, pwm value
# Outputs: N/A
##########################################
def set_motor(self, pwm_val):
    lgpio.tx_pwm(self, MOTOR, FREQ, pwm_val)

########################################## 
# Setup function to intialize IMU and motor
# Inputs: N/A
# Outputs: Motor instance, IMU instance
##########################################
def setup():
    i2c = I2C
    bno = BNO055.BNO055(i2c=i2c)
    bno.begin()
    #calibrate_sensor(bno=bno)

    #Read calibration data from file
    file = open("calibration_data.txt",'rb')
    calibration_data = file.read(22)
    bno.set_calibration(calibration_data)
    file.close()

    calibrate_sensor(bno=bno)
    print("Successfully automated calibration!!")
    time.sleep(1)

    h = lgpio.gpiochip_open(0)
    arm(h)

    return h, bno

########################################## 
# Stops the motor. Must be run at end of program
# Inputs: Motor instance
# Outputs: N/A
##########################################
def stop_motor(self):
    print("Stopping motor")
    lgpio.tx_pwm(self, MOTOR, FREQ, MIN_SIGNAL)
    time.sleep(10)
    lgpio.gpio_write(self, MOTOR, 0)
    lgpio.gpiochip_close(self)

########################################## 
# Arms the motor. Must be run before powering the motor
# Inputs: handle to gpio chip device (h)
# Outputs: N/A
##########################################
def arm(self):
    print("Sending minimum output")
    lgpio.tx_pwm(self, MOTOR, FREQ, MIN_SIGNAL)
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