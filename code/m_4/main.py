# CircuitPython demo - I2C scan

import time

import board
import busio

#  mentioned, board.I2C() is just shorthand for busio.I2C(board.SCL, board.SDA).
# Use one or the other but not both. Once one grabs the pins, the other one wont' work. For simple use, always use board.I2C().


i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass

while True:
    print("I2C addresses found:", [hex(device_address)
                                   for device_address in i2c.scan()])
    time.sleep(2)
