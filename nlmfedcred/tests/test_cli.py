import os

from nlmfedcred.cli import main, output_creds
from nlmfedcred.fedcred import Credentials
from nlmfedcred.idp import DEFAULT_IDP

SBOX_MLB_CONFIG = """# awscreds config
[DEFAULT]
account = 070163433501
role = nlm_aws_users
username = markfu

[sbox-mlb]
idp = auth7.nih.gov
"""


def test_setup_certs(tmpdir):
    testbundle = str(tmpdir.join('test-bundle.pem'))
    if os.path.exists(testbundle):
        os.path.remove(testbundle)

    args = [
        'dummy',
        '--setupcerts',
        testbundle,
    ]
    rc = main(args=args)
    assert os.path.exists(testbundle)
    assert rc == 0


def test_samlout(tmpdir, mocker, samldata):
    samlout = str(tmpdir.join('samlout.b64'))
    if os.path.exists(samlout):
        os.path.remove(samlout)

    args = [
        'dummy',
        '--idp', 'idpauth.example.com',
        '--ca-bundle', 'test-bundle.pem',
        '--samlout', samlout
    ]

    getpass = mocker.patch('nlmfedcred.cli.getpass', return_value='fake password')
    make_idp = mocker.patch('nlmfedcred.cli.make_idp', return_value=DEFAULT_IDP)
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value=samldata)
    rc = main(args)
    assert rc == 0
    assert getpass.call_count == 1
    assert make_idp.call_count == 1
    assert get_saml_assertion.call_count == 1
    assert os.path.exists(samlout)
    assert 'REQUESTS_CA_BUNDLE' in os.environ
    assert os.environ['REQUESTS_CA_BUNDLE'] == 'test-bundle.pem'


def test_bad_password(mocker):
    args = [
        'dummy',
        '--password', 'fake password'
    ]
    getpass = mocker.patch('nlmfedcred.cli.getpass',
                           side_effect=RuntimeError('getpass should not be called'))
    make_idp = mocker.patch('nlmfedcred.cli.make_idp',
                            side_effect=RuntimeError('make_idp should not be called'))
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value='US-EN')
    write_error = mocker.patch('nlmfedcred.cli.sys.stderr.write', return_value=0)

    rc = main(args)

    assert rc == 1
    assert getpass.call_count == 0
    assert make_idp.call_count == 0
    assert get_saml_assertion.call_count == 1
    assert write_error.call_count == 1
    assert 'invalid password' in write_error.call_args[0][0]


def test_bash_out(tmpdir, mocker, samldata):
    output_file = str(tmpdir.join('awscreds.sh'))
    if os.path.exists(output_file):
        os.path.remove(output_file)
    args = [
        'dummy',
        '--output', output_file,
        '--shell', 'bash',
        '--account', '070163433501',
        '--role', 'nlm_aws_users',
    ]
    getpass = mocker.patch('nlmfedcred.cli.getpass', return_value='fake password')
    make_idp = mocker.patch('nlmfedcred.cli.make_idp',
                            side_effect=RuntimeError('make_idp should not be called'))
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value=samldata)

    expected_credentials = Credentials(access_key='7777', secret_key='8888', session_token='9999')
    assume_role = mocker.patch('nlmfedcred.cli.fedcred.assume_role_with_saml', return_value=expected_credentials)
    write_error = mocker.patch('nlmfedcred.cli.sys.stderr.write', return_value=0)
    output_creds_mm = mocker.patch('nlmfedcred.cli.output_creds', wraps=output_creds)
    save_creds = mocker.patch('nlmfedcred.cli.update_aws_credentials', return_value=0)

    rc = main(args)

    assert rc == 0
    assert getpass.call_count == 1
    assert make_idp.call_count == 0
    assert get_saml_assertion.call_count == 1
    assert write_error.call_count == 0
    assert assume_role.call_count == 1
    assert output_creds_mm.call_count == 1
    assert save_creds.call_count == 0


def test_named_profile(tmpdir, mocker, samldata):
    args = [
        'dummy',
        '--profile',
        'sbox-mlb'
    ]

    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(SBOX_MLB_CONFIG)
    getpass = mocker.patch('nlmfedcred.cli.getpass', return_value='fake-password')
    make_idp = mocker.patch('nlmfedcred.cli.make_idp', return_value=DEFAULT_IDP)
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value=samldata)

    expected_credentials = Credentials(access_key='7777', secret_key='8888', session_token='9999')

    assume_role = mocker.patch('nlmfedcred.cli.fedcred.assume_role_with_saml', return_value=expected_credentials)
    write_error = mocker.patch('nlmfedcred.cli.sys.stderr.write', return_value=0)
    get_awscreds_config_path = mocker.patch('nlmfedcred.config.get_awscreds_config_path', return_value=inipath)
    output_creds_mm = mocker.patch('nlmfedcred.cli.output_creds', wraps=output_creds)
    save_creds = mocker.patch('nlmfedcred.cli.update_aws_credentials', return_value=0)

    rc = main(args)

    assert rc == 0
    assert get_awscreds_config_path.call_count == 1
    assert getpass.call_count == 1
    assert make_idp.call_count == 1
    assert get_saml_assertion.call_count == 1
    assert write_error.call_count == 0
    assert assume_role.call_count == 1
    assert output_creds_mm.call_count == 0
    assert save_creds.called_once_with('us-east-1', expected_credentials, 'sbox-mlb', None)


def test_default_profile(tmpdir, mocker, samldata):
    args = [
        'dummy',
        '--profile',
    ]

    # build temporary configuration file
    inipath = tmpdir.join('config.ini')
    inipath.write(SBOX_MLB_CONFIG)
    getpass = mocker.patch('nlmfedcred.cli.getpass', return_value='fake-password')
    make_idp = mocker.patch('nlmfedcred.cli.make_idp', return_value=DEFAULT_IDP)
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value=samldata)

    expected_credentials = Credentials(access_key='7777', secret_key='8888', session_token='9999')

    assume_role = mocker.patch('nlmfedcred.cli.fedcred.assume_role_with_saml', return_value=expected_credentials)
    write_error = mocker.patch('nlmfedcred.cli.sys.stderr.write', return_value=0)
    get_awscreds_config_path = mocker.patch('nlmfedcred.config.get_awscreds_config_path', return_value=inipath)
    output_creds_mm = mocker.patch('nlmfedcred.cli.output_creds', wraps=output_creds)
    save_creds = mocker.patch('nlmfedcred.cli.update_aws_credentials', return_value=0)

    rc = main(args)

    assert rc == 0
    assert get_awscreds_config_path.call_count == 1
    assert getpass.call_count == 1
    assert make_idp.call_count == 0
    assert get_saml_assertion.call_count == 1
    assert write_error.call_count == 0
    assert assume_role.call_count == 1
    assert output_creds_mm.call_count == 0
    assert save_creds.called_once_with('us-east-1', expected_credentials, 'default', None)
