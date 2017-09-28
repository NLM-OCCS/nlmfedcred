import os
from configparser import ConfigParser
from nlmfedcred.idp import IDP, DEFAULT_IDP, make_idp


def parse_config(path, account, role):
    c = ConfigParser()
    if os.path.isfile(path):
        c.parse(path)
    return c
