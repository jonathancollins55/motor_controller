import lgpio
from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import time
import threading
import csv
import matplotlib.pyplot as plt

MOTOR = 12
FREQ = 50
MAX_SIGNAL = 90
MIN_SIGNAL = 50
STEP_SIZE = 2
TIME_START = time.time()
AXIS = 0 

def main():
    io_data = [[],[],[]]
    motor, bno = setup()

    try:
        accelerate(motor,bno,io_data)
        #decelerate(motor,bno,io_data)
        lgpio.gpiochip_close(motor)
    except KeyboardInterrupt:
        lgpio.gpiochip_close(motor)
        data_to_csv(io_data,"io_data.csv")
        generate_plot(io_data[2],io_data[1],"Input (Duty Cycle)","Output (Position in degrees)","io_data.png")
    

def get_position(bno):
    return bno.read_euler()[AXIS]

def accelerate(self,bno,io_data):
    for i in range(MIN_SIGNAL,MAX_SIGNAL,STEP_SIZE):
        pwm = i/10
        lgpio.tx_pwm(self, MOTOR, FREQ, pwm)
        print("Signal is", i)
        pos = get_position(bno)

        io_data[0].append(time.time()-TIME_START)
        io_data[1].append(pos)
        io_data[2].append(pwm)

        time.sleep(15)

def decelerate(self,bno,io_data):
    for i in range(MAX_SIGNAL,MIN_SIGNAL,-STEP_SIZE):
        pwm = i/10
        lgpio.tx_pwm(self, MOTOR, FREQ, pwm)
        print("Signal is", i)
        pos = get_position(bno)

        io_data[0].append(time.time()-TIME_START)
        io_data[1].append(pos)
        io_data[2].append(pwm)

        #time.sleep(1)

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

def arm(self):
    print("Sending minimum output")
    lgpio.tx_pwm(self, MOTOR, FREQ, MIN_SIGNAL)
    turn_on_power = input("Turn on power source and press any key")
    time.sleep(3)

    print("Finished Arming")

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

def data_to_csv(data,filename):
    file = open(filename, 'w+', newline ='')            
    with file:   
        write = csv.writer(file)
        write.writerows(data)
    file.close()

def generate_plot(x,y,x_label,y_label,filename,y2=None,y3=None):
    plt.plot(x,y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if(y2 != None): plt.plot(x,y2)
    if(y3 != None): plt.plot(x,y3)
    plt.savefig(filename)

    plt.close()

if __name__ == "__main__":
    main()