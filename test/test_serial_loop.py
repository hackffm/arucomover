import serial.tools.list_ports
import sys

from time import sleep

device = '/dev/ttyACM0'

def write(ser, command):
    command = str(command) + '\r'
    ser.write(command.encode())


def serial_read(ser):
    sleep(0.1)
    data = b''

    wait_bytes = ser.inWaiting()
    print(str(wait_bytes) + ' bytes waiting in serial port')
    for i in range(ser.inWaiting()):
        b = ser.read(1)
        if b != b'\r':
            if b == b'\n':
                return data
            else:
                data += b
    return False


def serial_active(device_name):
    for p in ports:
        if  p.device == device_name:
            return True
    return False


print('search used serial ports')
ports = list(serial.tools.list_ports.comports())
if len(ports) == 0:
    print('no used ports found')
    sys.exit()
    
if not serial_active(device):
    print(device + ' is not part of active ports')
    sys.exit()

for i in range(1000):
    print('{}   write to device {}'.format(str(i),device))
    ser = serial.Serial(device, 38400)
    write(ser, 'led13')
    sr = serial_read(ser)
    if isinstance(sr, bool):
        sr = str(sr)
    else:
        sr = str(sr.decode())
    print('Serial result was ' + sr)

