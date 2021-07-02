
import helper_test

from config import Configuration
from helper import Helper

def main():
    name = 'arucodetection'
    configuration = Configuration(name='arucodetection', config_root=helper_test.config_root(name))
    config = configuration.config
    helper = Helper(configuration)

    _input = config['camera']['input']
    _input = config['input'][_input]
    print("configured camrea port is " + str(_input))

    print('Preconfiguration defaults')
    c_default = configuration.default_mode()
    print(c_default)

    print("configured default settings")
    for d in config['default']:
        print(str(d) + ":" + str(config['default'][d]))

    print('debug is ' + str(config['debug']))

    #
    print('configured camera is ' + config['camera']['name'])
    mtx, dist = configuration.camera_calibration()
    print(mtx)
    print(dist)

    print('camera default config')
    config['camera']['name'] = "default"
    mtx, dist = configuration.camera_calibration()
    print(mtx)
    print(dist)

    configuration = Configuration(name='evil', config_root='/notvalid')

if __name__ == '__main__':
    main()