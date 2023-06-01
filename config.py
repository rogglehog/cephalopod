from yaml import safe_load
from os.path import expanduser
from pathlib import Path
from shutil import copyfile

config_path = expanduser('~/.config/podcast_manager/config.yaml')

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
