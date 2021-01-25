"""
Test ability to parse configuration files
"""
import os

import pytest

from nlmfedcred.config import (get_home, get_user, parse_config,
                               setup_certificates)
from nlmfedcred.exceptions import ProfileNotFound

from . import restore_env, setup_awsconfig

JUST_DEFAULTS = '''# awscreds config
[DEFAULT]
account = 123456
role = nlm_aws_geek
duration = 7200
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
duration = 14400

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
    c = parse_config(None, None, None, None, None, None, inipath=str(inipath))

    # so we still have nothing
    assert c.account is None
    assert c.role is None
    assert c.idp is None
    assert c.duration == 3600
    assert c.subject is None


def test_file_not_found(tmpdir):
    # file does not exist
    inipath = tmpdir.join('config.ini')

    # we provide arguments
    c = parse_config(None, 99999, 'nlm_aws_users', None, 'authtest.nih.gov', None, inipath=str(inipath))

    # expect the arguments
    assert c.account == '99999'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'authtest.nih.gov'
    assert c.duration == 3600
    assert c.subject is None


def test_parses_defaults(tmpdir):

    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(JUST_DEFAULTS)

    # parse config with no command-line options
    c = parse_config(None, None, None, None, None, None, inipath=str(inipath))

    # should have the defaults
    assert c.account == '123456'
    assert c.role == 'nlm_aws_geek'
    assert c.idp == 'authfu.nih.gov'
    assert c.duration == 7200


def test_specified_trumps_default(tmpdir):
    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(JUST_DEFAULTS)

    # parse configuration with all command-line options
    c = parse_config(None, '99999', 'nlm_aws_users', 7208, 'authtest.nih.gov', None, inipath=str(inipath))

    # expect what was provided
    assert c.account == '99999'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'authtest.nih.gov'
    assert c.duration == 7208


def test_defaults_with_realfile():
    c = parse_config(None, '99999', 'nlm_aws_users', None, 'authtest.nih.gov', None)

    # expect what was provided
    assert c.account == '99999'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'authtest.nih.gov'
    assert c.duration == 3600


def test_realistic(tmpdir):
    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(REALISTIC_CONFIG)

    # Parse configuration with 'NLM-QA' profile
    c = parse_config('NLM-QA', None, None, None, None, None, inipath=str(inipath))

    # expect NLM-QA settings
    assert c.account == '777777'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'auth7.nih.gov'
    assert c.username == 'markfu'
    assert c.duration == 3600

    # Do it again for another profile
    c = parse_config('NLM-INT', None, 'nlm_aws_admin', None, None, None, inipath=str(inipath))
    assert c.account == '888888'
    assert c.role == 'nlm_aws_admin'
    assert c.idp == 'auth8.nih.gov'
    assert c.username == 'markfu'
    assert c.duration == 14400


def test_realistic_profilenotfound(tmpdir):
    inipath = tmpdir.join('config.ini')
    inipath.write(REALISTIC_CONFIG)
    with pytest.raises(ProfileNotFound):
        parse_config('nosuchprofile', None, None, None, None, None, inipath=str(inipath))


def test_default_inipath(tmpdir, mocker):
    # mocks the function used to load the default inipath, to make sure that is called and works
    inipath = tmpdir.join('config.ini')
    inipath.write(REALISTIC_CONFIG)
    mocker.patch('nlmfedcred.config.get_awscreds_config_path', return_value=str(inipath))
    c = parse_config('NLM-QA', None, None, None, None, None)
    assert c.account == '777777'
    assert c.role == 'nlm_aws_users'
    assert c.idp == 'auth7.nih.gov'
    assert c.username == 'markfu'
    assert c.ca_bundle is None
    assert c.duration == 3600


def test_ca_bundle_none_none(tmpdir, mocker):
    awsconfig = str(tmpdir.join('aws-config'))
    if os.path.exists(awsconfig):
        os.remove(awsconfig)

    mocker.patch('nlmfedcred.config.get_aws_config_path', return_value=awsconfig)
    c = parse_config('default', None, None, None, None, None, ca_bundle=None)      # being explicit
    assert c.ca_bundle is None


def test_ca_bundle_takes_aws_over_none(tmpdir, mocker):
    mockbundle = str(tmpdir.join('mock-bundle.pem'))
    awsconfig = setup_awsconfig(tmpdir, mockbundle)

    mocker.patch('nlmfedcred.config.get_aws_config_path', return_value=awsconfig)
    c = parse_config('default', None, None, None, None, None)
    assert c.ca_bundle == mockbundle


def test_ca_bundle_takes_provided_over_aws(tmpdir, mocker):
    mockbundle = str(tmpdir.join('mock-bundle.pem'))
    awsconfig = setup_awsconfig(tmpdir, mockbundle)

    mocker.patch('nlmfedcred.config.get_aws_config_path', return_value=awsconfig)
    c = parse_config('default', None, None, None, None, None, ca_bundle='override-bundle')
    assert c.ca_bundle == 'override-bundle'


def test_setup_creds_initial(tmpdir):
    # THis is more of a didn't blow up test, there's not much to test other than it writes the file
    testbundle = str(tmpdir.join('test-bundle.pem'))
    if os.path.exists(testbundle):
        os.path.remove(testbundle)

    setup_certificates(testbundle)

    assert os.path.exists(testbundle)
