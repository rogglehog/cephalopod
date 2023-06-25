from yaml import safe_load
from os.path import expanduser
from pathlib import Path
from shutil import copyfile

config_path = expanduser('./doc/config.yaml')

# try to read config file
# copy default if it doesnt exist
def load_config():
    try:
        with open(config_path, 'r') as config:
            return safe_load(config)
    except FileNotFoundError:
        print('No config file found. Adding default to', config_path, '\n')
        Path(config_path).parent.mkdir(exist_ok=True, parents=True)
        copyfile('./doc/config.yaml', config_path)
        with open(config_path, 'r') as config:
            return safe_load(config)

def test_config(key):
    config = load_config()
    try:
        return config['general'][key]
    except KeyError:
        print('Problem reading config.', key, 'missing')
