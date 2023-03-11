# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#! /usr/bin/python3.10
height = 10.61
serial_port = 'COM4'
import os
import time
import sys
from math import atan
print("Interpreter: ", sys.executable)
print("library path: ", sys.path)
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import serial
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
#cs = digitalio.DigitalInOut(board.D5)
# create the mcp object
mcp = MCP.MCP3008(spi, 0)
# create an analog input channel on pin 0
mos_chan1 = AnalogIn(mcp, MCP.P1)
mos_chan2 = AnalogIn(mcp, MCP.P0)
mos_chan3 = AnalogIn(mcp, MCP.P2)
### Arduino code conversion here: ###
# digital pin numbers, set pinMode(1,OUTPUT)
mos_1a = digitalio.DigitalInOut(board.D17)
mos_1a.direction = digitalio.Direction.OUTPUT
mos_1b = digitalio.DigitalInOut(board.D27)
mos_1b.direction = digitalio.Direction.OUTPUT
mos_1c = digitalio.DigitalInOut(board.D22)
mos_1c.direction = digitalio.Direction.OUTPUT

mos_2a = digitalio.DigitalInOut(board.D13)
mos_2a.direction = digitalio.Direction.OUTPUT
mos_2b = digitalio.DigitalInOut(board.D19)
mos_2b.direction = digitalio.Direction.OUTPUT
mos_2c = digitalio.DigitalInOut(board.D26)
mos_2c.direction = digitalio.Direction.OUTPUT
# digitalWrite(1,LOW)
mos_1a.value = False
mos_1b.value = False
mos_1c.value = False
mos_2a.value = False
mos_2b.value = False
mos_2c.value = False
# set serial, we can use it like this:
# line = ser.readline()
# string = line.decode() << to make this into a string
# ser = serial.Serial(serial_port,9600, timeout=1)
# values of the intensity levels
values = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]
counter = 0
muxChannel = [[1,1,0], # channel 3
        [0,0,0], # channel 0
        [1,0,0], # channel 1
        [0,1,0], # channel 2
        [0,0,1], # channel 4
        [0,1,1], # channel 6
        [1,1,1], # channel 7
        [1,0,1]] # channel 5
# print('Raw ADC Value: ', chan0.value)
# print('ADC Voltage: ' + str(chan0.voltage) + 'V')

def readMux_1(channel):
        controlPin = []
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
def readMux_2(channel):
        controlPin = []
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
def printArray():
        for i in range(16):
                print(values[0][i], " //index ", values[1][i])

def angleMeasure():
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

def initialize():
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

#max = initialize()
# max = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
print(max)
while True:
        for i in range(10):
                for mos1 in range(8):
                        values[0][mos1] = readMux_1(mos1) #max[mos1]-readMux_1(mos1)
                        values[1][mos1] = (8-mos1)*(-1)
                for mos2 in range(8):
                        values[0][mos2+8] = readMux_2(mos2)# max[mos2+8] - readMux_2(mos2) 
                        values[1][mos2+8] = mos2+1
        print("Full Array:")
        printArray()
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # print("Angle:")
        # angle = angleMeasure()
        # print(angle)
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        time.sleep(0.5)
