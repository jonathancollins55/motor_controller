import board
import busio
import serial
import time

port = '/dev/ttyAMA0'
baudrate = 9600
parity = serial.PARITY_ONE
bits = serial.EIGHTBITS
stopbits = serial.STOPBITS_ONE

i2c = busio.I2C(board.SCL,board.SDA)
#uart = busio.UART(board.TX,board.RX,buadrate=9600)

byte_one = bytes.fromhex('DD')
byte_two = bytes.fromhex('64')
send_bytes = bytearray([221,100])
stop_command = bytes.fromhex('FF')

print("Past initializations")

def main():
    ser = serial_start()
    ser.write(send_bytes)
    time.sleep(5)
    stop_motor(ser)

def serial_start():
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate
    ser.timeout = 5
    ser.parity = parity
    ser.bytesize = bits
    ser.stopbits = stopbits
    ser.open()
    time.sleep(2)
    return ser

def stop_motor(ser):
    cmd = bytes.fromhex('FF')
    ser.write(cmd)

if __name__ == "__main__":
    main()
