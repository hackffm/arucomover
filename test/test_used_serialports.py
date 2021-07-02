import serial.tools.list_ports
from time import sleep


def write(ser, command):
    command = str(command) + '\r'
    ser.write(command.encode())


def serial_read(ser):
    sleep(1.0)
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


print('search used serial ports')
ports = list(serial.tools.list_ports.comports())
if len(ports) == 0:
    print('no used ports found')
for p in ports:
    print('write to ' + p.description + ' on port ' + p.device)
    ser = serial.Serial(p.device, 38400)
    write(ser, '?')
    sr = serial_read(ser)
    if isinstance(sr, bool):
        sr = str(sr)
    else:
        sr = str(sr.decode())
    print('Serial result was ' + sr)

