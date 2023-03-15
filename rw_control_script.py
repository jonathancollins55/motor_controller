from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import lgpio
import time
import RW_Controller

###################################
# Variables - Controller
###################################
KP = 1/100
KI = 0
KD = 0

###################################
# Other Variables
###################################
AXIS = 0                #Axis to slew on
TARGET_POSITION = 90    #relative target position (in degrees clockwise)
E_MAX = 1.5             #Maximum tolerable steady-state error

MOTOR = 12
FREQ = 50
STOP_SIGNAL = 7.5
# MAX_SIGNAL = 10
# MIN_SIGNAL = 5
# STEP_SIZE = .001

########################################## 
# Main Function
# Inputs: None
# Outputs: None
##########################################
def main():
    motor, bno = setup()
    target_position = get_target_position(bno=bno)

    print("target position is:",target_position)
    time.sleep(2)
    print("Starting control")
    time.sleep(3)

    controller = RW_Controller.RW_Controller(KP,KI,KD,E_MAX,bno)

    controller.jot_and_plot()

    while(True):
        try:
            #Get PWM signal
            pwm = controller.control(target_position)
            set_motor(motor,pwm)
            time.sleep(.5)

        except KeyboardInterrupt:
            print()
            print("Terminating Program...")
            time.sleep(1)
            stop_motor(motor)

            controller.jot_and_plot()

            break

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

    #Read calibration data from file
    file = open("calibration_data.txt",'rb')
    calibration_data = file.read(22)
    bno.set_calibration(calibration_data)
    file.close()

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
    lgpio.tx_pwm(self, MOTOR, FREQ, STOP_SIGNAL)
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
    lgpio.tx_pwm(self, MOTOR, FREQ, STOP_SIGNAL)
    turn_on_power = input("Turn on power source and press any key")
    time.sleep(3)

    print("Finished Arming")

########################################## 
# Run Main function from command line
##########################################
if __name__ == "__main__":
    main()
