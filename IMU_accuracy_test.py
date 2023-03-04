from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import time
import csv
import matplotlib.pyplot as plt
import numpy as np

def main():
    pointing_data = [[],[],[]]  #time, real_pointing, measured_pointing

    i2c = I2C
    bno = BNO055.BNO055(i2c=i2c)
    bno.begin()
    
    file = open("calibration_data.txt",'rb')
    calibration_data = file.read(22)
    bno.set_calibration(calibration_data)
    file.close()
    print("Calibrated!")
    time.sleep(1)

    tare_zero = bno.read_euler()[0]

    for i in range(24):
        pointing = (bno.read_euler()[0] - tare_zero)     #Yaw axis
        if (pointing < tare_zero): measured_pointing = 360 + pointing - tare_zero
        else: measured_pointing = pointing - tare_zero
        pointing_data[0].append(i+1)
        pointing_data[1].append(15*i)
        pointing_data[2].append(measured_pointing)
        print("True pointing:",(i+1)*15)
        print("Measured pointing:", measured_pointing)
        print("Turn IMU now!")
        time.sleep(4)
        print("Finished turning")

    data_to_csv(pointing_data,"IMU_Accuracy_Test.csv")
    generate_plot(pointing_data[0],pointing_data[1],"Time (Normalized)","Pointing Angle (in degreess)","IMU_Accuracy_Test.png",measured_pointing)

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


########################################## 
# Run Main function from command line
##########################################
if __name__ == "__main__":
    main()