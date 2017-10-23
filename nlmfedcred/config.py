from configparser import ConfigParser
from collections import namedtuple
import os
import certifi
from io import StringIO
import hashlib
import shutil

__all__ = ('Config', 'parse_config', 'get_user', 'get_home',)


Config = namedtuple('Config', ('account', 'role', 'idp', 'username',))


def parse_config(profile, account, role, idp, username, inipath=None):

    if inipath is None:
        inipath = os.path.join(get_home(), '.getawscreds')

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
        home_path = os.path.expanduser('~')
    return home_path


def setup_certs():
    certifi_bundle = certifi.where()
    our_bundle = os.path.join(get_home(), '.getawscreds-cacert.pem')
    if not os.path.exists(our_bundle):
        # if our own copy does not exist, make a copy
        shutil.copyfile(certifi_bundle, our_bundle)
    elif os.stat(certifi_bundle).st_mtime > os.stat(our_bundle).st_mtime:
        # if our own copy is older, make a copy
        shutil.copyfile(certifi_bundle, our_bundle)
    our_cert_data = nlmsecpalo_cert()
    assure_cert_in_bundle(our_cert_data, our_bundle)
    os.environ.setdefault('REQUESTS_CA_BUNDLE', our_bundle)


def assure_cert_in_bundle(cert_data, bundle_path):
    if not certsfile_hascert(bundle_path, cert_data):
        with open(bundle_path, 'a') as f:
            f.write(cert_data)


def checksum(certdata):
    return hashlib.md5(certdata.encode('ascii')).hexdigest()


def certsfile_hascert(path, certdata):
    oursum = checksum(certdata)
    matching_certs = list(filter(lambda c: c == oursum, map(checksum, enum_certs(path))))
    return len(matching_certs) > 0


def nlmsecpalo_cert():
    with open(os.path.join(os.path.dirname(__file__), 'certs/nlmsecpalo.pem'), 'r') as cert_file:
        return cert_file.read()


def enum_certs(path):
    with open(path, 'r') as cert_file:
        buf = StringIO()
        for line in cert_file:
            s = line.rstrip()
            if s == '-----BEGIN CERTIFICATE-----':
                buf = StringIO()
            buf.write(line)
            if s == '-----END CERTIFICATE-----':
                certificate = buf.getvalue()
                buf = StringIO()
                yield certificate
