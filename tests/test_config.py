"""
Test ability to parse configuration files
"""
from nlmfedcred.config import parse_config, get_user, get_home
import os

from . import restore_env

JUST_DEFAULTS = '''# awscreds config
[DEFAULT]
account = 123456
role = nlm_aws_geek
idp = authfu.nih.gov
'''

REALISTIC_CONFIG = '''# awscreds config
[DEFAULT]
role = nlm_aws_users
username = markfu

[NLM-QA]
account = 777777
idp = auth7.nih.gov

[NLM-INT]
account = 888888
idp = auth8.nih.gov
'''


@restore_env
def test_default_user():
    expect_user = 'mbarking'
    os.environ['USER'] = expect_user
    actual_user = get_user()

    assert expect_user == actual_user


@restore_env
def test_default_username():
    expect_user = 'mbarking'
    if 'USER' in os.environ:
        os.environ.pop('USER')
    os.environ['USERNAME'] = expect_user
    actual_user = get_user()

    assert expect_user == actual_user


@restore_env
def test_get_home_anyunix():
    if 'HOME' in os.environ:
        os.environ.pop('HOME')
    os.environ['HOMEDRIVE'] = 'C:'
    os.environ['HOMEPATH'] = '\\Users\\mbarking'
    actual_homedir = get_home()
    assert 'C:\\Users\\mbarking' == actual_homedir


@restore_env
def test_get_home_windows():
    if 'HOMEDRIVE' in os.environ:
        os.environ.pop('HOMEDRIVE')
    if 'HOMEPATH' in os.environ:
        os.environ.pop('HOMEPATH')
    expect_homedir = '/home/mbarking'
    os.environ['HOME'] = expect_homedir
    actual_homedir = get_home()
    assert expect_homedir == actual_homedir


def test_none_none(tmpdir):
    # filename does not exist
    inipath = tmpdir.join('config.ini')

    # neither do arguments
    c = parse_config(None, None, None, None, None, str(inipath))

    # so we still have nothing
    assert c.account is None
    assert c.role is None
    assert c.idp is None


def test_file_not_found(tmpdir):
    # file does not exist
    inipath = tmpdir.join('config.ini')

    # we provide arguments
    c = parse_config(None, 99999, 'nlm_aws_users', 'authtest.nih.gov', None, str(inipath))

    # expect the arguments
    assert c.account == '99999'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'authtest.nih.gov'


def test_parses_defaults(tmpdir):

    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(JUST_DEFAULTS)

    # parse config with no command-line options
    c = parse_config(None, None, None, None, None, str(inipath))

    # should have the defaults
    assert c.account == '123456'
    assert c.role == 'nlm_aws_geek'
    assert c.idp == 'authfu.nih.gov'


def test_specified_trumps_default(tmpdir):
    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(JUST_DEFAULTS)

    # parse configuration with all command-line options
    c = parse_config(None, '99999', 'nlm_aws_users', 'authtest.nih.gov', None, str(inipath))

    # expect what was provided
    assert c.account == '99999'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'authtest.nih.gov'


def test_defaults_with_realfile():
    c = parse_config(None, '99999', 'nlm_aws_users', 'authtest.nih.gov', None)

    # expect what was provided
    assert c.account == '99999'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'authtest.nih.gov'


def test_realistic(tmpdir):
    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(REALISTIC_CONFIG)

    # Parse configuration with 'NLM-QA' profile
    c = parse_config('NLM-QA',  None, None, None, None, str(inipath))

    # expect NLM-QA settings
    assert c.account == '777777'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'auth7.nih.gov'
    assert c.username == 'markfu'

    # Do it again for another profile
    c = parse_config('NLM-INT', None, 'nlm_aws_admin', None, None, str(inipath))
    assert c.account == '888888'
    assert c.role == 'nlm_aws_admin'
    assert c.idp == 'auth8.nih.gov'
    assert c.username == 'markfu'

    # Test what happens if the section is not found
    c = parse_config('NLM-PROD', None, None, None, None, str(inipath))
    assert c.account is None
    assert c.role == 'nlm_aws_users'
    assert c.idp is None
    assert c.username == 'markfu'
