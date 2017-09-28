from configparser import ConfigParser
from collections import namedtuple
import os


Config = namedtuple('Config', ('account', 'role', 'idp',))


def parse_config(profile, account, role, idp, inipath=None):

    if inipath is None:
        inipath = os.path.join(os.path.expanduser('~'), '.getawscreds')

    config = ConfigParser()
    config.read(inipath)

    if profile is not None and profile in config:
        section = profile
    else:
        section = 'DEFAULT'

    if account is None:
        account = config.get(section, 'account', fallback=None)
        if account is not None:
            account = int(account)

    if role is None:
        role = config.get(section, 'role', fallback=None)

    if idp is None:
        idp = config.get(section, 'idp', fallback=None)

    return Config(account, role, idp)
