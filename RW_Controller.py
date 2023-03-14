import time, csv
import numpy as np
import matplotlib.pyplot as plt
from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C

#Controller class for ESC and reaction wheel using BNO055 IMU for attitude estimation
#Controls slewing angle for single axis
class RW_Controller:

    MOTOR = 12              #PWM GPIO pin ESC is connected to
    FREQ = 50               #Frequency of PWM signal
    MAX_SIGNAL = 10         #MAX PWM% of ESC
    STOP_SIGNAL = 7.5       #PWM% to stop and arm ESC
    MIN_SIGNAL = 5          #MIN PWM% of ESC

    AXIS = 0                #Slewing axis, used for IMU attitude estimations

    ########################################## 
    # Initialize controller instance
    # Inputs: self, kp, ki, kd, bno_imu
    # Outputs: None
    ##########################################
    def __init__(self, kp, ki, kd, bno_imu) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.bno_imu = bno_imu
        self.curr_pos = self.get_position(bno_imu)
        self.prevT = 0
        self.currT = 0
        self.time_start = time.time()
        self.eprev = 0
        self.e_integral = 0
        self.pwm_prev = self.STOP_SIGNAL
        self.error_data = [[],[]]
        self.io_data = [[],[],[]]

    ########################################## 
    # Single Control instance. Calculates control input
    # Inputs: Control instance
    # Outputs: PWM signal to send to ESC
    ##########################################
    def control(self, target_angle):
        #Time difference
        self.currT = time.time_ns()
        if (self.prevT == 0): deltaT = 0
        else: deltaT = (self.currT-self.prevT)/10**9    #Time difference adjusted to seconds
        self.prevT = self.currT

        #error
        self.curr_pos = self.get_position(self.bno_imu)
        e = target_angle -self.curr_pos

        #Calculate integral and derivative of error
        dedt = (e-self.eprev)/deltaT
        e_integral = self.e_integral + e*deltaT

        print("e:", e)
        print("dedt:", dedt)
        print("e_int:", e_integral)

        #Update error and integral of error
        self.eprev = e
        self.e_integral = e_integral

        #Determine turning direction
        turnClockwise = self.isClockwise(target_angle,e)
        print("isClockwise:",turnClockwise)

        #Calculate control signal
        if (e < 1.5):
            u = 0
            pwm = self.pwm_prev
        else:
            u = self.kp*e
            # u = self.kp*e + self.ki*self.e_integral + self.kd*dedt
            pwm = self.pwm_prev + turnClockwise*u

        print("Control signal is:", u)
        print("PWM is:", pwm)

        #Bound control output
        if (pwm > 10): pwm = self.MAX_SIGNAL
        if (pwm < 5): pwm = self.MIN_SIGNAL

        #Plotting Error
        self.error_data[0].append(time.time()-self.time_start)
        self.error_data[1].append(e)

        #Plotting Input, Output
        self.io_data[0].append(time.time()-self.time_start)
        self.io_data[1].append(pwm)
        self.io_data[2].append(self.curr_pos)


        return pwm
    
    def isClockwise(self, e):
        e_mag = np.abs(e)
        if((e >= 0 and e_mag <= 180) or (e < 0 and e_mag > 180)):
            return -1   #Clockwise turn
        else:
            return 1    #CCW turn

    ########################################## 
    # Returns current position of sensor
    # Inputs: BNO055 sensor
    # Outputs: position on specified axis
    ##########################################
    def get_position(bno):
        return bno.read_euler()[RW_Controller.AXIS]
    
    ########################################## 
    # Returns IO data of controller as CSV
    # Inputs: Controller instance
    # Outputs: CSV file
    ##########################################
    def get_IO_data(self):
        self.data_to_csv(self.io_data,"io_data.csv")      #Writing IO data into file

    ########################################## 
    # Returns Error data of controller as CSV
    # Inputs: Controller instance
    # Outputs: CSV file
    ##########################################
    def get_error_data(self):
        self.data_to_csv(self.error_data,"e_plot.csv")    #Writing error data into file

    ########################################## 
    # Plots error data as PNG
    # Inputs: Controller instance
    # Outputs: PNG file
    ##########################################
    def plot_error(self):
        self.generate_plot(self.error_data[0],self.error_data[1],"Time (in seconds)", "Error (in degrees)","error.png")

    ########################################## 
    # Plots IO data as PNG
    # Inputs: Controller instance
    # Outputs: PNG file
    ##########################################
    def plot_IO(self):
        self.generate_plot(self.io_data[1],self.io_data[2],"Input (duty cycle)","Position (in degrees)","io.png")


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
    # Outputs list data of error and IO as csv file, as well as error and IO graphs as png image
    # Inputs: Controller instance
    # Outputs: CSV, PNG
    ##########################################
    def jot_and_plot(self):
        self.get_IO_data()
        self.get_error_data()
        self.plot_error()
        self.plot_IO()