from configparser import ConfigParser
from collections import namedtuple
import os

__all__ = ('Config', 'parse_config', 'get_user', 'get_home',)


Config = namedtuple('Config', ('account', 'role', 'idp', 'username',))


def parse_config(profile, account, role, idp, username, inipath=None):

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
        account = str(account)

    if role is None:
        role = config.get(section, 'role', fallback=None)
    if role is not None:
        role = str(role)

    if idp is None:
        idp = config.get(section, 'idp', fallback=None)
    if idp is not None:
        idp = str(idp)

    if username is None:
        username = config.get(section, 'username', fallback=get_user())
        username = str(username)

    return Config(account, role, idp, username)


def get_user():
    '''
    Get the current username in a way that should work in Linux, OS X, and Windows
    '''
    if 'USER' in os.environ:
        # shell in Linux/OS X
        username = os.environ['USER']
    elif 'USERNAME' in os.environ:
        # shell in Windows
        username = os.environ['USERNAME']
    else:
        # crontab in Linux/OS X, may not work with setuid/setgid programs.
        # We assume a login shell changes semantics; this is by design
        username = os.getlogin()
    return username


def get_home():
    '''
    Get the home directory of the user in a way that should work in Linux, OS X, and Windows
    '''
    if 'HOME' in os.environ:
        home_path = os.environ['HOME']
    elif 'HOMEDRIVE' in os.environ and 'HOMEPATH' in os.environ:
        home_path = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    else:
        home_path = None
    return home_path
