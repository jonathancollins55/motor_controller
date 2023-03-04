from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import time
import csv
import matplotlib.pyplot as plt

def main():
    pointing_data = [[],[],[]]  #time, real_pointing, measured_pointing

    i2c = I2C
    bno = BNO055.BNO055(i2c=i2c)
    bno.begin()
    calibrate_sensor(bno)

    while(True):
        if(bno.calibrated()): break
        else: print("BNO055 not fully calibrated")

    tare_zero = bno.read_euler()[0]

    for i in range(24):
        print("Turn IMU now!")
        time.sleep(3)
        print("Finished turning")
        measured_pointing = (bno.read_euler()[0] - tare_zero)     #Yaw axis
        pointing_data[0].append(i+1)
        pointing_data[1].append((i+1)*15)
        pointing_data[2].append(measured_pointing)
        print("True pointing:",(i+1)*15)
        print("Measured pointing:", measured_pointing)

    data_to_csv(pointing_data,"IMU_accuracy.csv")
    generate_plot(pointing_data[0],pointing_data[1],"Time (Normalized)","Pointing Angle (in degreess)","IMU_Accuracy_Test.png",pointing_data[2])



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


########################################## 
# Run Main function from command line
##########################################
if __name__ == "__main__":
    main()