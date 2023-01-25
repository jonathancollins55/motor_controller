import serial
import time

device = '/dev/ttyS0'

ser = serial.Serial(device,9600,timeout=5)

byte_one = bytes.fromhex('DD')
byte_two = bytes.fromhex('64')
send_bytes = bytearray([byte_one,byte_two])
stop_command = bytes.fromhex('FF')

ser.write(send_bytes)
time.sleep(5)
ser.write(stop_command)