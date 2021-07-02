# -*- coding: utf-8 -*-
import codecs
import json
import numpy as np
import os
import sys


class Configuration:

    def __init__(self, name, config_root='../'):
        self.config_name = name
        self.config_path = config_root

        self.config = []
        self.load(self.config_path + 'config.json')

    def load(self, config_path):
        print('load config from', config_path)
        if os.path.exists(config_path):
            with open(config_path) as json_data:
                j_config = json.load(json_data)
            self.config = j_config[self.config_name]
        else:
            print('config file %s not found' % config_path)
            print('see in ../shell/setup for an example')
            sys.exit(1)

    # -- config ------------------------------------------------------------------
    def camera_calibration(self):
        _calibration_name = self.config['camera']['name']
        path_calibration = self.config_path + '/' + _calibration_name + '.json'
        # default if not other config found
        mtx = np.array([[5.3434144579284975e+02, 0., 3.3915527836173959e+02],
                        [0., 5.3468425881789324e+02, 2.3384359492532246e+02],
                        [0., 0., 1.]], float)
        dist = np.array([-2.8832098285875657e-01, 5.4107968489116441e-02,
                         1.7350162244695508e-03, -2.6133389531953340e-04,
                         2.0411046472667685e-01], float)
        if os.path.exists(path_calibration):
            with codecs.open(path_calibration, 'r', encoding='utf-8') as pc:
                obj_text = pc.read()
                j_camera_config = json.loads(obj_text)
                mtx = np.array(j_camera_config['camera_matrix'])
                dist = np.array(j_camera_config['dist_coeff'])
        return [mtx, dist]

    def default_mode(self):
        _mode = {"detect": {"id": 0, "position": "0,0,0"}}
        return _mode
