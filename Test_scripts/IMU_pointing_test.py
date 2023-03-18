from Adafruit_BNO055 import BNO055
import Adafruit_GPIO.I2C as I2C
import time
import csv
import matplotlib.pyplot as plt
import numpy as np
import math

def main():
    pointing_data = [[],[],[],[]]  #time, real_pointing, measured_pointing

    bno = setup()
    bno.begin()
    
    #calibrate_sensor(bno)
    #time.sleep(5)

    for i in range(5):
        true_pointing = 10*i
        reset = input("Reset to 0 degrees")
        start_attitude = bno.read_euler()[0]    #0 = Yaw axis
        prompt_str = "Turn " + str(true_pointing) + " degrees"
        turn_now = input(prompt_str)
        end_attitude = bno.read_euler()[0]

        turn_degrees = start_attitude - end_attitude

        error = true_pointing - turn_degrees

        pointing_data[0].append(10*i)
        pointing_data[1].append(error)
        
        print("True pointing:",10*i)
        print("Error:", error)
        print("Finished turning")

    data_to_csv(pointing_data,"IMU_Pointing_Test.csv")
    generate_plot(pointing_data[0],pointing_data[1],"Turning Degree","Error","IMU_Pointing_Test.png",pointing_data[2])

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
    return bno

def data_to_csv(data,filename):
    file = open(filename, 'w+', newline ='')            
    with file:   
        write = csv.writer(file)
        write.writerows(data)
    file.close()

def generate_plot(x,y,x_label,y_label,filename,y2=None,y3=None):
    plt.plot(x,y,'bo')
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if(y2 != None): plt.plot(x,y2)
    if(y3 != None): plt.plot(x,y3)
    plt.savefig(filename)

    plt.close()
 
def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

def quat_to_angle(quat,zero_quat):
    roll, pitch, yaw = euler_from_quaternion(quat[0],quat[1],quat[2],quat[3])
    roll_0, pitch_0, yaw_0 = euler_from_quaternion(zero_quat[0],zero_quat[1],zero_quat[2],zero_quat[3])

    if (pitch < pitch_0): output = 2*np.pi + pitch - pitch_0
    else: output = pitch - pitch_0

    return np.degrees(output)


########################################## 
# Run Main function from command line
##########################################
if __name__ == "__main__":
    main()