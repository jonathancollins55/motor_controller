import board
import busio
import time

uart = busio.UART(board.TX,board.RX,buadrate=9600)

byte_one = bytes.fromhex('DD')
byte_two = bytes.fromhex('64')
send_bytes = bytearray([221,100])
stop_command = bytes.fromhex('FF')


def main():
    uart.write(send_bytes)
    time.sleep(5)
    stop_motor()

def stop_motor():
    cmd = bytes.fromhex('FF')
    uart.write(cmd)

if __name__ == "__main__":
    main()
