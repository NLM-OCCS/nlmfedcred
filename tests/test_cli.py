import os
from nlmfedcred.cli import execute_from_command_line
from nlmfedcred.idp import DEFAULT_IDP
from nlmfedcred.fedcred import Credentials

from .fixtures import *


def test_setup_certs(tmpdir):
    testbundle = str(tmpdir.join('test-bundle.pem'))
    if os.path.exists(testbundle):
        os.path.remove(testbundle)

    args = [
        'dummy',
        '--setupcerts',
        testbundle,
    ]
    rc = execute_from_command_line(args=args)
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
    rc = execute_from_command_line(args)
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
    getpass = mocker.patch('nlmfedcred.cli.getpass', return_value='fake password')
    make_idp = mocker.patch('nlmfedcred.cli.make_idp', return_value=DEFAULT_IDP)
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value='US-EN')
    write_error = mocker.patch('nlmfedcred.cli.sys.stderr.write', return_value=0)

    rc = execute_from_command_line(args)

    assert rc == 1
    assert getpass.call_count == 0
    assert make_idp.call_count == 0
    assert get_saml_assertion.call_count == 1
    assert write_error.call_count == 1
    assert 'invalid password' in write_error.call_args[0][0]


def test_normal_flow(tmpdir, mocker, samldata):
    output_file = str(tmpdir.join('awscreds.sh'))
    if os.path.exists(output_file):
        os.path.remove(output_file)
    args = [
        'dummy',
        '--output', output_file,
        '--shell', 'bash',
        '--account', '070163433501'
    ]
    getpass = mocker.patch('nlmfedcred.cli.getpass', return_value='fake password')
    make_idp = mocker.patch('nlmfedcred.cli.make_idp', return_value=DEFAULT_IDP)
    get_saml_assertion = mocker.patch('nlmfedcred.cli.fedcred.get_saml_assertion', return_value=samldata)

    expected_credentials = Credentials(access_key='7777', secret_key='8888', session_token='9999')
    assume_role = mocker.patch('nlmfedcred.cli.fedcred.assume_role_with_saml', return_value=expected_credentials)
    write_error = mocker.patch('nlmfedcred.cli.sys.stderr.write', return_value=0)

    rc = execute_from_command_line(args)

    assert rc == 0
    assert getpass.call_count == 1
    assert make_idp.call_count == 0
    assert get_saml_assertion.call_count == 1
    assert write_error.call_count == 0
    assert assume_role.call_count == 1
