# functions that do configuration, session management + generic functions

import os
import sys

import yaml
from shutil import copy2 as cp
import json

__all__ = ['encode', 'config', 'session']

from rubecula.logging import console


def encode(msg):
    if not isinstance(msg, bytes):
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        msg = msg.encode()
    return msg


def get_config():
    if not os.path.exists('config.yaml'):
        if os.path.exists("config.yaml.example"):
            cp('config.yaml.example', 'config.yaml')
        else:
            console.error("No config.yaml or config.yaml.example could be found. "
                          "Please create one in the project's root folder!")
            exit(1)

    with open('config.yaml') as stream:
        yaml_config = yaml.load(stream, Loader=yaml.FullLoader)

    console.loglevel = yaml_config.get('log')

    return yaml_config


def write_config(c_dict):
    with open('config.yaml', 'w') as f:
        yaml.dump(c_dict, f, default_flow_style=False)


config = get_config()

session = {
}  # session storage
