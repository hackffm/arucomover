import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(file_dir)
dir_lr = os.path.join(parent_dir, 'local_ressources')
sys.path.append(dir_lr)
dir_ac = os.path.dirname(parent_dir + '/code')
sys.path.append(dir_ac)


def config_root(name):
    home = os.getenv('HOME')
    c_path = home + '/' + name + '/'
    return c_path


def file_delete(file_name):
    if os.path.exists(file_name):
        print('remove ' + file_name)
        os.remove(file_name)
