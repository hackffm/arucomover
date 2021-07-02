import numpy as np
import os
import sys
import time

from multiprocessing import Process, Queue, Lock
from multiprocessing import Manager
from multiprocessing import shared_memory

from local_ressources import Camera
from local_ressources import Configuration
from local_ressources import Helper
from webserver import WebServer

l_lock = Lock()
q_message = Queue()
m_modus = ''


def config_root(name_program):
    home = os.getenv('HOME')
    c_path = home + '/' + name_program + '/'
    return c_path


def handle_message(msg):
    if msg.startswith('do:'):
        msg = msg[3:]
        if msg == 'shutdown':
            helper.state_save()
            log(msg)
            time.sleep(1.0)
            return False
    else:
        log(msg)
        return True


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


if __name__ == '__main__':
    name = 'arucodetection'
    configuration = Configuration(name=name, config_root=config_root(name))
    helper = Helper(configuration)
    logHome = helper.log_home(name)

    debug = configuration.config['debug']
    log('debug is ' + str(debug))
    running = True

    # start
    handle_message('do:start')
    if logHome == configuration.config['error']:
        print('Error:can not create default log files')
        print('check you config.json')
        sys.exit()

    frame_height, frame_width = helper.camera_config()

    shm_video_name, shm_handle = shared_memory_array(name, frame_height, frame_width)
    if shm_video_name == 'Error':
        sys.exit(1)
    video_config = {"shm_video_name": shm_video_name, "height": str(frame_height), "width": str(frame_width)}

    try:
        with Manager() as manager:
            m_modus = manager.dict()
            m_modus['detect'] = {"id": "0", "position": "0,0,0"}
            helper.dict_copy(configuration.default_mode(), m_modus)
            # start processes
            p2 = Process(target=WebServer, args=(name, l_lock, configuration, helper, q_message, m_modus, video_config))
            p2.daemon = True
            p2.start()

            # startup info to console
            log('start running')
            helper.state_set_start()
            infos = helper.infos_self()
            for info in infos:
                print(info)
            log('PID arucudetection ' + str(os.getpid()))
            log('PID Webserver ' + str(p2.pid))

            # prepare camera
            camera = Camera(configuration, helper, m_modus, shm_handle)
            cap = camera.capture_config()
            if cap is False:
                log('Error: failed to initialise camera')
                running = False

            # main loop
            while running:
                try:
                    camera.detect_aruco(cap)
                    message = ''
                    if not q_message.empty():
                        message = q_message.get()
                        if message != '':
                            running = handle_message(message)
                except Exception as e:
                    log('error in Main loop ' + str(e))
                    print('error in Main loop ' + str(e))
                    running = False
            # exit
    except KeyboardInterrupt:
        log('ending with keyboard interrupt')
        p2.terminate()
        cap.release()
    except Exception as e:
        log('error in arucodetection __main__ ' + str(e))
        print('error in arucodetection __main__ ' + str(e))

    shm_handle.close()
    shm_handle.unlink()
    infos = helper.state_updated()
    for info in infos:
        print(info)
        log(info)
    log('stopped running---------------------------------------')
    sys.exit()
