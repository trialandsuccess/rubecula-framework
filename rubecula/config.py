# functions that do configuration, session management + generic functions

import os
import yaml
from shutil import copy2 as cp
import json

__all__ = ['encode', 'config', 'session']


def encode(msg):
    if not isinstance(msg, bytes):
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        msg = msg.encode()
    return msg


def get_config():
    # fixme

    if not os.path.exists("config.yaml.example"):
        return {}

    if not os.path.exists('config.yaml'):
        cp('config.yaml.example', 'config.yaml')
    with open('config.yaml') as stream:
        yaml_config = yaml.load(stream, Loader=yaml.FullLoader)
    return yaml_config


def write_config(c_dict):
    with open('config.yaml', 'w') as f:
        yaml.dump(c_dict, f, default_flow_style=False)


config = get_config()

session = {
}  # session storage
