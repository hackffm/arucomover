import numpy as np
import os
import time

import helper_test

from multiprocessing import Process, Queue, Lock
from multiprocessing import Manager
from multiprocessing import shared_memory

from local_ressources import Camera
from local_ressources import Configuration
from local_ressources import Helper


def config_root(name_program):
    home = os.getenv('HOME')
    c_path = home + '/' + name_program + '/'
    return c_path


def log(text):
    global name
    helper.log_add_text(name, 'main:' + text)


def shared_memory_array(name_aditional, hight, width):
    _name = 'shm_' + name_aditional
    a = np.random.rand(hight, width)
    try:
        shm = shared_memory.SharedMemory(name=_name, create=True, size=a.nbytes)
        return [_name, shm]
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=_name, create=False, size=a.nbytes)
        return [_name, shm]
    except Exception as shm_e:
        log('Error:' + str(shm_e))
        print('Error:' + str(shm_e))
        return ["Error", None]


name = 'arucodetection'
configuration = Configuration(name=name, config_root=config_root(name))
helper = Helper(configuration)
m_modus = ''

frame_height, frame_width = helper.camera_config()

shm_video_name, shm_handle = shared_memory_array(name, frame_height, frame_width)

with Manager() as manager:
    m_modus = manager.dict()
    m_modus['detect'] = {"id": "0", "position": "0,0,0"}

    # prepare camera
    camera = Camera(configuration, helper, m_modus, shm_handle)
    cap = camera.capture_config()
    print('debug is ' + str(camera.debug))
    helper.state_set_start()
    start = time.time()

    camera.detect_aruco(cap)

    end = time.time()
    log('camera duration ' + str(end - start))
    infos = helper.state_updated()
    for info in infos:
        print(info)
        log(info)


cap.release()
shm_handle.close()
shm_handle.unlink()