import hashlib
import os
import shutil
from collections import namedtuple
from configparser import ConfigParser
from io import StringIO

import certifi

from .exceptions import CertificatesFileNotFound, ProfileNotFound

__all__ = (
    'Config',
    'parse_config',
    'get_user',
    'get_home',
    'get_aws_config_path',
    'get_aws_credentials_path',
    'update_aws_credentials',
)


Config = namedtuple('Config', ('account', 'role', 'duration', 'idp', 'username', 'subject', 'ca_bundle'))


def parse_config(
        profile=None,
        account=None,
        role=None,
        duration=None,
        idp=None,
        username=None,
        ca_bundle=None,
        subject=None,
        inipath=None):

    defaults = None
    awspath = get_aws_config_path()
    if os.path.exists(awspath):
        preconfig = ConfigParser()
        preconfig.read(awspath)
        defaults = preconfig['default']

    if inipath is None:
        inipath = get_awscreds_config_path()

    config = ConfigParser(defaults=defaults)
    config.read(inipath)

    if profile is not None and profile in config:
        section = profile
    elif profile is None or profile == 'default':
        section = 'DEFAULT'
    else:
        raise ProfileNotFound("Profile '{}' not found in confuguration".format(profile))

    if account is None:
        account = config.get(section, 'account', fallback=None)
    if account is not None:
        account = str(account)

    if role is None:
        role = config.get(section, 'role', fallback=None)
    if role is not None:
        role = str(role)

    if duration is None:
        duration = config.get(section, 'duration', fallback=3600)
        duration = int(duration)

    if idp is None:
        idp = config.get(section, 'idp', fallback=None)
    if idp is not None:
        idp = str(idp)

    if subject is None:
        subject = config.get(section, 'subject', fallback=None)
    if subject is not None:
        subject = str(subject)

    if ca_bundle is None:
        ca_bundle = config.get(section, 'ca_bundle', fallback=None)
    if ca_bundle is not None:
        ca_bundle = str(ca_bundle)

    if username is None:
        username = config.get(section, 'username', fallback=get_user())
        username = str(username)

    return Config(account, role, duration, idp, username, subject, ca_bundle)


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


def get_aws_config_path():
    # This function exists to allow mocking during test plans
    return os.path.join(get_home(), '.aws', 'config')


def get_aws_credentials_path():
    # This function exists to allow mocking during test plans
    return os.path.join(get_home(), '.aws', 'credentials')


def get_awscreds_config_path():
    # THis function exists to allow mocking during test plans
    return os.path.join(get_home(), '.getawscreds')


def setup_certificates(bundle_path):
    """
    Copy the certificates in certifi package to our own name
    Append our SSL interceptors certificate to the set of certificates in certifi
    Define REQUESTS_CA_BUNDLE to point towards that.
    """
    certifi_bundle = certifi.where()
    if not os.path.exists(certifi_bundle):
        raise CertificatesFileNotFound()
    shutil.copyfile(certifi_bundle, bundle_path)
    our_cert_data = nlmsecpalo_cert()
    assure_cert_in_bundle(our_cert_data, bundle_path)


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


def update_aws_credentials(region, creds, profile='default', path=None):
    config = ConfigParser()
    if not path:
        path = get_aws_credentials_path()
    dirname = os.path.dirname(path)
    if os.path.isdir(dirname):
        config.read(path)
    else:
        os.mkdir(dirname)
    config.remove_section(profile)
    config.add_section(profile)
    config.set(profile, 'region', region)
    config.set(profile, 'aws_access_key_id', creds.access_key)
    config.set(profile, 'aws_secret_access_key', creds.secret_key)
    config.set(profile, 'aws_session_token', creds.session_token)
    print('Updating profile "%s" in ~/.aws/credentials' % profile)
    with open(path, 'w') as fp:
        config.write(fp)
