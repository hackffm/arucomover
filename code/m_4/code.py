import board
import microcontroller
import pulseio
import supervisor
import sys
import time

import adafruit_bh1750
import adafruit_bme680
import adafruit_bno055
from adafruit_motorkit import MotorKit
from digitalio import DigitalInOut, Direction, Pull
from time import sleep

# -- hardware-------------------------------------------------------------------
i2c = board.I2C()
kit = MotorKit()

#
led_cycle = 65535
#led_green = pulseio.PWMOut(board.D7, frequency=5000, duty_cycle=0)
#led_red = pulseio.PWMOut(board.D9, frequency=5000, duty_cycle=0)


led_13 = DigitalInOut(board.D13)
led_13.direction = Direction.OUTPUT

# sensor bh1750 light
sensor_bh1750 = adafruit_bh1750.BH1750(i2c)

# sensor bme680 air
sensor_bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
sensors_bme680 = ["gas", "humidity", "pressure", "temperature"]

# sensor BNO055 IMU
sensor_bno055 = adafruit_bno055.BNO055_I2C(i2c)
sensors_bno055 = ["acceleration","calibration_status","euler","gravity","gyro","heading",
        "linear_acceleration","magnetic","quaternion","temperature"]

# btm01
btm01 = DigitalInOut(board.D2)
btm01.direction = Direction.INPUT
btm01.pull = Pull.UP

# constants
btm_pushed = 'pushed'
btm_pushed_not = 'not pushed'
node_name = 'base1'

# defaults
cmd_line = ""
cycle_count = 0                # used to count up for cycle_short
cycle_global = 10000.00        # all commands reset to stop after this cycle
cycle_short = 10               # comands redo or stop after short time
heading_current = 0
heading_set = 0
running = True
state_btm01 = btm_pushed_not
state_led_13 = False
state_logger = False
state_motor = [0.0,0.0]         # power for motor [left, right]
time_ns = time.monotonic_ns()
velocity_max = 1.0              # velocity_max limits power to the motors
velocity_run  = 0.8             # velocity_run means power to be set for both motors
velocity_stop = 0.0             # velocity_stop means no power to be set for both motors
print('start ' + node_name)
# -- commands --------------------------------------------------------------------
def cmd_base(arg):
    global state_motor
    global cycle_count
    speed = [velocity_stop,velocity_stop]
    if type(arg) != str:
        return
    if arg == "turn_left":
        speed = [velocity_run,-velocity_run]
        cycle_count = 7
    if arg == "turn_right":
        speed = [-velocity_run,velocity_run]
        cycle_count = 7
    if arg == "forward":
        speed = [velocity_run,velocity_run]
        cycle_count = 0
    if arg == "backward":
        speed = [-velocity_run,-velocity_run]
        cycle_count = 0
    if arg == "stop":
        speed = [velocity_stop,velocity_stop]
        cycle_count = 9
    state_motor = speed
    return #cmd_base


def cmd_id():
    text = node_name + ':'
    for command in cmd_dict:
        text = text + command + ','
    text = text[:-1]
    print(text)
    return


def cmd_btm01(arg):
    global state_btm01
    module_name = node_name + ':btm01:'
    print(module_name + state_btm01)
    state_btm01 = btm_pushed_not
    cmd_led13(False)
    return


def cmd_heading(arg):
    global heading_current
    module_name = node_name + ':heading:'
    heading_current = euler_get_x()
    if arg == "p":
        print(module_name + str(heading_current))


def cmd_i2c(arg):
    module_name = node_name + ':i2c:'
    while not i2c.try_lock():
        pass
    print(module_name + " addresses found:", [hex(device_address)for device_address in i2c.scan()])
    i2c.unlock()


def cmd_led13(arg):
    global state_led_13
    module_name = node_name + ':led13:'
    if arg != "":
        arg = bool(arg)
        state_led_13 = arg
    else:
        if state_led_13 == False:
            state_led_13 = True
        else:
            state_led_13 = False
    led_13.value = state_led_13
    print(module_name + str(state_led_13))


def cmd_logger(arg):
    global state_logger
    if arg != "":
        state_logger = arg
        return
    if state_logger:
        state_logger = False
    else:
        state_logger = True
    return


def cmd_motor(arg):
    global state_motor
    module_name = node_name + ':motor:'
    arg_1 = velocity_stop
    arg_2 = velocity_stop
    if len(arg) > 0:
        try:
            if "," in arg:
                arg_1, arg_2 = arg.split(",")
                arg_1 = float(arg_1)
                arg_1 = limit_value(arg_1)
                arg_2 = float(arg_2)
                arg_2 = limit_value(arg_2)
                state_motor = [arg_1, arg_2]
            else:
                arg = float(arg)
                state_motor = [arg, arg]
        except Exception as e:
            print(module_name + 'exception:' + str(e))
    print(module_name + str(state_motor))
    return # cmd_motor

def cmd_sensor_bh1750(arg):
    module_name = node_name + ':sensor_bh1750:'
    print(module_name + "Light:%.2f" % sensor_bh1750.lux)

def cmd_bme680(arg):
    arg = arg.lower()
    module_name = node_name + ':sensor_bme680:'
    if arg in sensors_bme680:
        result = getattr(sensor_bme680, arg)
        print("sensor_bme680:" + arg + ":" + str(result))
    if arg == "p":
        print(module_name + 'Temperature:{}'.format(sensor_bme680.temperature))
        print(module_name + 'Gas:{}'.format(sensor_bme680.gas))
        print(module_name + 'Humidity:{}'.format(sensor_bme680.humidity))
        print(module_name + 'Pressure:{}'.format(sensor_bme680.pressure))

def cmd_sensor_bno055(arg):
    arg = arg.lower()
    module_name = node_name + ':sensor_bno055:'
    if arg in sensors_bno055:
        result = getattr(sensor_bno055, arg)
        print(module_name + arg + ":" + str(result))
    if arg == "p":
        print(module_name + "accelerometer:{}".format(sensor_bno055.acceleration))
        print(module_name + "CalibrationStatus:{}".format(sensor_bno055.calibration_status))
        print(module_name + "euler:{}".format(sensor_bno055.euler))
        print(module_name + "gravity:{}".format(sensor_bno055.gravity))
        print(module_name + "gyroscope:{}".format(sensor_bno055.gyro))
        print(module_name + "acceleration:{}".format(sensor_bno055.linear_acceleration))
        print(module_name + "magnetometer:{}".format(sensor_bno055.magnetic))
        print(module_name + "quaternion:{}".format(sensor_bno055.quaternion))
        print(module_name + "temperature:{}".format(sensor_bno055.temperature))
    return


def cmd_stop(arg):
    if not arg:
        arg = node_name
    module_name = arg + ':stop'
    motor_stop(module_name)
    cmd_logger(False)
    cmd_led13("")
    time_reset()


def cmd_temperature(arg):
    module_name = node_name + ':temperature:'
    temp = str(microcontroller.cpu.temperature)
    print(module_name + temp)


def cmd_timer(arg):
    # timer for max process len of all
    global cycle_global
    module_name = node_name + ':timer:'
    if arg != '':
        try:
            cycle_global = float(arg)
        except Exception as e:
            print(module_name + 'exception:' + str(e))
            return
        print(module_name + 'cycle_global:' + str(cycle_global))
    else:
        print(module_name + 'time diff:' + str(cmd_uptime("_")))
    return # time1


def cmd_uptime(args):
    global time_ns
    module_name = node_name + ':uptime:'
    time_now = time.monotonic_ns()
    diff = (time_now - time_ns)
    diff = diff / 1000000
    if args == '_':
        return diff
    else:
        print(module_name + str(diff))


# --end of commands --------------------------------------------------------------------
def cycle_check():
    global cycle_count
    global state_btm01
    global state_logger
    global state_motor
    module_name = node_name + ':cycle_check:'
    if btm01.value:
        # we ask here if btm01 pushed as it could be used as kill switch else where
        state_btm01 = btm_pushed

    td = cmd_uptime('_')
    if td > cycle_global:
        print(module_name + 'stop')
        cmd_stop(node_name)
        cmd_sensor_bh1750("p")
        cmd_bme680("p")
        cmd_sensor_bno055("p")
        cmd_temperature("")
        cycle_count = 0
    else:
        if cycle_count >= cycle_short:
            state_motor = [velocity_stop,velocity_stop]
            cycle_count = 0
        else:
            cycle_count = cycle_count + 1
    motor_run(state_motor)
    return # cycle_check


def euler_get_x():
    se = str(sensor_bno055.euler)
    se = se.replace("(","")
    se = se.replace(")","")
    se = se.replace(" ","")
    se = se.split(",")[0]
    if se == "None":
        # catch pesky i2c outages
        return
    se = se.split(".")[0]
    se = int(se)
    return se


def limit_value(value):
    if value > velocity_max:
        return velocity_max
    if value < -velocity_max:
        return -velocity_max
    return value


def motor_run(arg):
    global heading_current
    kit.motor4.throttle = arg[0]
    #led_red.duty_cycle = led_cycle
    kit.motor1.throttle = arg[1]
    #led_green.duty_cycle = led_cycle
    return


def motor_stop(arg):
    global state_motor
    if not 'silent' in arg:
        print(node_name + ':motor:stop')
    state_motor = [velocity_stop,velocity_stop]
    kit.motor4.throttle = 0
    #led_red.duty_cycle = 0
    kit.motor1.throttle = 0
    #led_green.duty_cycle = 0


def serial_process_command(command):
    if len(command) == 1:
        if command[0] == '?':
            cmd_id()
    else:
        _cmd = ''
        _arg = ''
        if ':' in command:
            command = command.split(':')
            _cmd = command[0]
            _arg = command[1]
        else:
            _cmd = command
        if _cmd in cmd_dict:
            cmd_dict[_cmd](_arg)
            time_reset()
        else:
            print(":unkown command=>" + str(command))
    return # serial_process_command


def serial_receive_cmd():
    global cmd_line
    if supervisor.runtime.serial_bytes_available:
        value = sys.stdin.read(1)
        ch = ord(value)
        if 32 <= ch <= 126:           # printable character
            cmd_line += chr(ch)
        elif ch in {10, 13}:          # EOL - try to process
            serial_process_command(cmd_line)
            cmd_line = ''
    return # serial_receive_cmd


def time_reset():
    global time_ns
    time_ns = time.monotonic_ns()


if __name__ == '__main__':
    cmd_dict = {
      'base': cmd_base,
      'btm01': cmd_btm01,
      'heading': cmd_heading,
      'i2c': cmd_i2c,
      'led13': cmd_led13,
      'logger': cmd_logger,
      'motor': cmd_motor,
      'stop': cmd_stop,
      'sensor_bno055.': cmd_sensor_bno055,
      'temperature': cmd_temperature,
      'timer': cmd_timer,
      'uptime':cmd_uptime
    }
    count = 0
    while running:
            count += 1
            if count >= 1000:
                print(node_name + ':alive:' + str(time.monotonic()))
                count = 0
            serial_receive_cmd()
            cycle_check()
            sleep(0.1)