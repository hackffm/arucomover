import helper_test

from config import Configuration
from helper import Helper
from multiprocessing import Manager

name = 'arucodetection'
configuration = Configuration(name='arucodetection', config_root=helper_test.config_root(name))
config = configuration.config
helper = Helper(configuration)

print('Preconfiguration defaults')
c_default = configuration.default_mode()
print(c_default)

with Manager() as manager:
    print('copy dict')
    m_modus = manager.dict()
    helper.dict_copy(configuration.default_mode(), m_modus)
    print(m_modus)

print(helper.log_path)