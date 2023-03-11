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
KP = 1/360000
KI = 0
KD = 0

PREVT = 0
EPREV = 0
EINTEGRAL = 0
PWM_PREV = 7.5

###################################
# Other Variables
###################################
AXIS = 0                #Axis to slew on
TARGET_POSITION = 90    #relative target position (in degrees clockwise)
AXIS_REMAP_X = 0x00
AXIS_REMAP_Y = 0x01
AXIS_REMAP_Z = 0x02

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 10
SIGNAL_STOP = 7.5
MIN_SIGNAL = 5
STEP_SIZE = .001

########################################## 
# Main Function
# Inputs: None
# Outputs: None
##########################################
def main():
    ###################################
    # Variables - Controller
    ###################################
    KP = 1/360000
    KI = 0
    KD = 0

    PREVT = 0
    EPREV = 0
    EINTEGRAL = 0
    PWM_PREV = 7

    ###################################
    # Other Variables
    ###################################
    AXIS = 0                #Axis to slew on
    TARGET_POSITION = 90    #relative target position (in degrees clockwise)
    AXIS_REMAP_X = 0x00
    AXIS_REMAP_Y = 0x01
    AXIS_REMAP_Z = 0x02

    MOTOR = 12
    FREQ = 50
    MAX_SIGNAL = 10
    SIGNAL_STOP = 7.5
    MIN_SIGNAL = 5
    STEP_SIZE = .001


    current_position = 0

    motor, bno = setup()
    target_position = get_target_position(bno=bno)

    print("target position is:",target_position)
    time.sleep(2)
    print("Starting control")
    time.sleep(3)

    #FOR ERROR PLOTTING
    error_data = [[],[]]        #Error
    io_data = [[],[],[]]        #FOR SYSTEM ANALYZER
    gyro_data = [[],[],[],[]]   #For analyzing relationship with pwm signal
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

            #gyro vals
            gyro = bno.read_gyroscope()

            dedt = (e-EPREV)/deltaT
            eint = EINTEGRAL + e*deltaT

            #Calculate control signal
            if (e < 1.5):
                u = 0
                pwm = PWM_PREV
            else:
                u = KP*e
                pwm = PWM_PREV - u

            #Bound control output
            if (pwm > 10): pwm = MAX_SIGNAL
            if (pwm < 5): pwm = MIN_SIGNAL

            #Plotting Error
            error_data[0].append(time.time()-TIME_START)
            error_data[1].append(e)

            #Plotting Input, Output
            io_data[0].append(time.time()-TIME_START)
            io_data[1].append(pwm)
            io_data[2].append(current_position)

            #Plotting gyroscope data
            gyro_data[0].append(time.time()-TIME_START)
            gyro_data[1].append(gyro[0])
            gyro_data[2].append(gyro[1])
            gyro_data[3].append(gyro[2])

            print("Error:",e,"Control_Signal:",pwm)
            #print("Gyroscope value", bno.read_gyroscope()[axis])
            set_motor(motor,pwm)    #Put in await function. Continuously monitor error and change PID vals, but slowly change PWM
            #time.sleep(1)
            PWM_PREV = pwm
            EINTEGRAL = EINTEGRAL + eint

        except KeyboardInterrupt:
            print()
            print("Terminating Program...")
            time.sleep(1)
            stop_motor(motor)

            data_to_csv(error_data,"e_plot.csv")    #Writing error data into file
            data_to_csv(io_data,"io_data.csv")      #Writing IO data into file
            data_to_csv(gyro_data,"gyro.csv")       #Writing gyro data into file

            generate_plot(error_data[0],error_data[1],"Time (in seconds)", "Error (in degrees)","error.png")
            generate_plot(io_data[1],io_data[2],"Input (duty cycle)","Position (in degrees)","io.png")
            generate_plot(gyro_data[0],gyro_data[1],"Time (in seconds)","Radians/s","gyro.png",y2=gyro_data[2],y3=gyro_data[3])

            break

########################################## 
# Returns current position of sensor
# Inputs: BNO055 sensor
# Outputs: position on specified axis
##########################################
def get_position(bno):
    return bno.read_euler()[AXIS]

########################################## 
# Function to get angle of desired position
# Inputs: BNO055 sensor
# Outputs: absolute target position
##########################################
def get_target_position(bno):
    turn_degree = TARGET_POSITION % 360
    current_position = bno.read_euler()[AXIS]

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
    time.sleep(3)
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
#2D Plot Generator, outputs plot to file
# Inputs: x-data (array or list), y-data (array or list), x_label (string), y_label (string), filename (string)
# Outputs: None
##########################################
def generate_plot(x,y,x_label,y_label,filename,y2=None,y3=None):
    plt.plot(x,y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if(y2 != None): plt.plot(x,y2)
    if(y3 != None): plt.plot(x,y3)
    plt.savefig(filename)

    plt.close()

########################################## 
# Outputs list data to csv file
# Inputs: data (list or array), filename (string)
# Outputs: None
##########################################
def data_to_csv(data,filename):
    file = open(filename, 'w+', newline ='')            
    with file:   
        write = csv.writer(file)
        write.writerows(data)
    file.close()

########################################## 
# Run Main function from command line
##########################################
if __name__ == "__main__":
    main()
