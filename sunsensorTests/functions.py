# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#! /usr/bin/python3.10

############################## LIBRARIES ################################

import os
import time
import sys
import csv
from math import atan
# print("Interpreter: ", sys.executable)
# print("library path: ", sys.path)
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

############################## SETUP PINS ################################

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the mcp object
mcp = MCP.MCP3008(spi, 0)

# Channel 1 and Channel 0 for MCP3008 inputs from multiplexers
mos_chan1 = AnalogIn(mcp, MCP.P1)
mos_chan2 = AnalogIn(mcp, MCP.P0)

# Setup for Digital pin outputs for multiplexer 1
mos_1a = digitalio.DigitalInOut(board.D17)
mos_1a.direction = digitalio.Direction.OUTPUT
mos_1b = digitalio.DigitalInOut(board.D27)
mos_1b.direction = digitalio.Direction.OUTPUT
mos_1c = digitalio.DigitalInOut(board.D22)
mos_1c.direction = digitalio.Direction.OUTPUT

# Setup for Digital pin outputs for multiplexer 2
mos_2a = digitalio.DigitalInOut(board.D13)
mos_2a.direction = digitalio.Direction.OUTPUT
mos_2b = digitalio.DigitalInOut(board.D19)
mos_2b.direction = digitalio.Direction.OUTPUT
mos_2c = digitalio.DigitalInOut(board.D26)
mos_2c.direction = digitalio.Direction.OUTPUT

############################## INITIALIZE VALUES ################################

height = 10.61
serial_port = 'COM4'
if len(sys.argv) == 2:
        function_name = sys.argv[1] 
else:
        function_name = ""
# Start all multiplexer outputs to zero
mos_1a.value = False
mos_1b.value = False
mos_1c.value = False
mos_2a.value = False
mos_2b.value = False
mos_2c.value = False

# Set up values table to take in photodiode intensities
values = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]

# muxChannel pins for different channels
muxChannel = [[1,1,0], # channel 3
        [0,0,0], # channel 0
        [1,0,0], # channel 1
        [0,1,0], # channel 2
        [0,0,1], # channel 4
        [0,1,1], # channel 6
        [1,1,1], # channel 7
        [1,0,1]] # channel 5

############################## FUNCTIONS ################################

# Read in inputs only for multiplexer 1
def readMux_1(channel):
        if muxChannel[channel][0] == 1:
                mos_1a.value = True
        else:
                mos_1a.value = False
        if muxChannel[channel][1] == 1:
                mos_1b.value = True
        else:
                mos_1b.value = False
        if muxChannel[channel][2] == 1:
                mos_1c.value = True
        else:
                mos_1c.value = False
        return mos_chan1.value
    
# Read in inputs only for multiplexer 2
def readMux_2(channel):
        if muxChannel[channel][0] == 1:
                mos_2a.value = True
        else:
                mos_2a.value = False
        if muxChannel[channel][1] == 1:
                mos_2b.value = True
        else:
                mos_2b.value = False
        if muxChannel[channel][2] == 1:
                mos_2c.value = True
        else:
                mos_2c.value = False
        return (mos_chan2.value)
    
# Print all values of photodiodes, just raw values, usually dark is around 65472 and fully lit up is 0
def printArray():
        for mos1 in range(8):
                values[0][mos1] = readMux_1(mos1) 
                values[1][mos1] = (8-mos1)*(-1)
        for mos2 in range(8):
                values[0][mos2+8] = readMux_2(mos2)
                values[1][mos2+8] = mos2+1
        for i in range(16):
                print(values[0][i], " //index ", values[1][i])

# Measure Angle of photodiodes
def angleMeasure():
        max = 65472 #initialize_whenDark()
        for mos1 in range(8):
                values[0][mos1] = max-readMux_1(mos1) #max[mos1]-readMux_1(mos1)
                values[1][mos1] = (8-mos1)*(-1)
        for mos2 in range(8):
                values[0][mos2+8] = max - readMux_2(mos2) # max[mos2+8] - readMux_2(mos2)
                values[1][mos2+8] = mos2+1
        total_current_distance = 0
        total_current = 0
        for i in range(16):
                distance = (values[1][i]*2.54)
                if distance < 0:
                        distance = distance + (2.54/2)
                else:
                        distance = distance - (2.54/2)
                total_current_distance  = total_current_distance + values[0][i]*distance
                total_current = total_current + values[0][i]
        print(values[0][0:16])
        print(total_current_distance)
        if total_current == 0:
                return 0
        else:
                normalized_current_distance = total_current_distance/total_current
                angle = atan(normalized_current_distance/(height-3.2))*4068/(71*-1)
                return angle

# Honestly, don't think we need this; from trial and error I got 65472 for max values for most
def initialize_whenDark():
        max = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        for i in range(10):
                for mos1 in range(8):
                        temp = readMux_1(mos1)
                        if temp > max[mos1]:
                                max[mos1] = temp
                for mos2 in range(8):
                        temp = readMux_2(mos1)
                        if temp > max[mos2+8]:
                                max[mos2+8] = temp
                time.sleep(0.1)
        return max

def calibrate():
        for mos1 in range(8):
                values[0][mos1] = readMux_1(mos1) 
                values[1][mos1] = (8-mos1)*(-1)
        for mos2 in range(8):
                values[0][mos2+8] = readMux_2(mos2)
                values[1][mos2+8] = mos2+1
        print("What is the name of this document? Make sure to write <name>.csv")
        docname = input()

        # steps is left to right, 1-4
        header = ["Steps", "p_-8","p_-7","p_-6","p_-5","p_-4","p_-3","p_-2","p_-1","p_1","p_2","p_3","p_4","p_5","p_6","p_7","p_8"]
        file = open('calibrationData//'+ str(docname), 'w', newline='')
        writer = csv.writer(file)
        writer.writerow(header)
        step = 0
        for i in range(3):
                print("When ready to start calibrating, press any button:")
                input1 = input()
                # create the csv writer
                for i in range(10):
                        full = [step] + values
                        writer.writerow(full)
                step = step + 1
        file.close();

# Just run any of main functions
def main():
        while True:
                if function_name == "print":
                # IF YOU WANT TO JUST PRINT FULL ARRAY
                        print("Full Array:")
                        printArray()
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                elif function_name == "angle":               
                # IF YOU WANT TO PRINT ANGLES
                        print("Angle:")
                        angle = angleMeasure()
                        print(angle)
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                else:
                        print("If you want to print raw values of the full array, use command:")
                        print("")
                        print("python functions.py print")
                        print("")
                        print("If you want to print the values of angles, use command:")
                        print("")
                        print("python functions.py angle")
                        break
                time.sleep(0.5)

if __name__ == '__main__':
    main()
    

