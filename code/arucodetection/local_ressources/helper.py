import datetime
import json
import netifaces
import os
import socket


class Helper:
    def __init__(self, configuration):
        self.configuration = configuration
        self.config = configuration.config

        self.default = self.config['default']
        self.config_modes = self.config['modes']

        _config_output = self.default['output']
        self.config_output = self.config[_config_output]

        self.name = self.default['name']
        self.log_path = self.log_home(self.name)
        self.headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        self.state = {'date_start': self.now(), 'mode': self.config['default']['mode'], 'previews_start': 0}

    def camera_config(self):
        config_camera = self.config['camera']
        frame_height = config_camera['frame_height']
        frame_width = config_camera['frame_width']
        return [frame_height, frame_width]

    def datetime_diff_from_string(self, dt_string):
        dt_now = self.datetime_from_string(self.now())
        dt_old = self.datetime_from_string(dt_string)
        delta = dt_now - dt_old
        delta_seconds = delta.total_seconds()
        return delta_seconds

    def datetime_from_string(self, text):
        dt = ''
        try:
            dt = datetime.datetime.strptime(text, self.config_output['file_format_time'])
        except ValueError:
            dt = datetime.datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.log_add_text('helper', 'Error[Helper]' + str(e))
        return dt

    # this can not be static !
    def dict_copy(self, source_modus, dest_modus):
        for k, v in source_modus.items():
            dest_modus[k] = v

    def folder_create_once(self, folder_path):
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            return True
        except IOError as e:
            self.log_add_text('helper', 'Error[Helper]' + str(e))
            return False

    def infos_self(self):
        infos = ['hostname ' + str(socket.gethostname()), 'PID ' + str(os.getpid())]
        ifaces = self.interfaces_self()
        for iface in ifaces:
            infos.append(iface)
        return infos

    def interfaces_first(self):
        ips = self.interfaces_self()
        # remove ipv6 from results
        for ip in ips:  
            if ':' not in ip:
                return ip
        return '127.0.0.1'

    def interfaces_self(self):
        ifaces = []
        for interface in netifaces.interfaces():
            if interface != 'lo':
                if 2 in netifaces.ifaddresses(interface):
                    _i = netifaces.ifaddresses(interface)
                    _i = _i[2][0]['addr']
                    if self.not_local(_i):
                        ifaces.append(_i)
                if 17 in netifaces.ifaddresses(interface):
                    _i = netifaces.ifaddresses(interface)
                    _i = _i[17][0]['addr']
                    if self.not_local(_i):
                        ifaces.append(_i)
                if 18 in netifaces.ifaddresses(interface):
                    _i = netifaces.ifaddresses(interface)
                    _i = _i[18][0]['addr']
                    if self.not_local(_i):
                        ifaces.append(_i)
        return ifaces

    def log_add_text(self, name, text):
        text = self.now_str() + ': ' + ' ' + str(text)

        if name == self.name:
            with open(self.log_path, 'a') as outfile:
                outfile.write(text + '\n')
        else:
            l_home = self.log_home(name)
            with open(l_home, 'a') as outfile:
                outfile.write(text + '\n')
        return

    def log_home(self, name):
        _config = self.default
        _log_location = _config['log_location']
        _log_file = _config['log_file']
        if name in self.config:
            _config = self.config[name]
            if 'log_location' in _config:
                _log_location = _config['log_location']
            if 'log_file' in _config:
                _log_file = _config['log_file']
        log_home_path = _log_location + '/' + _log_file
        self.folder_create_once(_log_location)
        return log_home_path

    def now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def now_str(self):
        return datetime.datetime.now().strftime(self.config_output['file_format_time'])

    # -- state --------------------------------------------------
    def state_updated(self):
        try:
            state = self.state_load()
            date_start = str(state['date_start'])
            dt_diff = str(self.datetime_diff_from_string(date_start))
            dt_diff = float(dt_diff)
            if dt_diff > 60.0:
                dt_diff = dt_diff / 60.0
                dt_diff = str("{:.2f}".format(dt_diff))
                dt_diff = dt_diff + " min"
            else:
                dt_diff = str(dt_diff)
            infos = ['started:' + date_start, 'Now: ' + str(self.now()), 'seconds running: ' + dt_diff]
            self.log_add_text('helper', 'state_updated:' + str(infos))
            return infos
        except Exception as e:
            self.log_add_text('helper', 'state_updated:' + str(e))
            return []

    def state_load(self):
        try:
            return self.state
        except Exception as e:
            self.log_add_text('helper', str(e))

    def state_save(self):
        try:
            data = str(json.dumps(self.state))
            self.log_add_text('helper', 'saved state ' + data)
            return
        except Exception as e:
            self.log_add_text('helper', str(self.state))
            self.log_add_text('helper', 'state_save:' + str(e))

    def state_set_start(self):
        self.state['date_start'] = str(self.now())
        self.state_save()

    # -- statics ------------------------------------------------
    @staticmethod
    def dict_same_structure(one, two):
        if len(one) != len(two):
            return False
        for item in one:
            if item not in two:
                return False
        return True

    @staticmethod
    def is_different_modus(old, new):
        changed = False
        if old['detect'] != new['detect']:
            changed = True
        return changed

    @staticmethod
    def file_exists(path_file):
        if not os.path.isfile(path_file):
            return False
        return True

    @staticmethod
    def not_local(ip):
        if ip != '127.0.0.1':
            return True
        return False

    @staticmethod
    def loop(count=1000000):
        while count >= 0:
            count -= 1
