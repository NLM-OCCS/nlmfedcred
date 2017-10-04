"""
Test that the output based on a set of credentials is correct.
"""
from nlmfedcred.cli import output_creds, output_roles
from collections import namedtuple
import os
from . import restore_env

try:
    from io import StringIO
except ImportError:
    from stringio import StringIO


MockCreds = namedtuple('MockCreds', ('access_key', 'secret_key', 'session_token'))
mockcreds = MockCreds('ASIAJENQPGE6WHKG37BA', 'WjWoEb963D8aYxw7xxIHHu8UtNAwt8RpKn+CB+Wo', 'FQoDYXdzEDYaDKND5rh8OTvGidXqxCKhAgg170toE3mEpi3EGGWe0lHQGiw5IL+A5RHnAbmHaJ5Idf4IHVrC2n37OpgOhS43QhSGGRtxLv6FM3szOlqItI7wG/RgxthmUbmUzNXq36VpzRm3qyW42l6pZY8hCr4Vd8llPCPW8DY5fQleMkWf2E5OWYQt+YnDDhvdYgaD5exbV9erRXEnr+CSScbhiThZMJdfKcXT0QQj5cwlx7PJbuoi7S3QCIIuU2i2dp6ARmu8P7t5rkJ+9u187UJZzARDwnxzxB5fI7VOson015uLZuz859+5QyAasgOaHTzgVbxaLVFVSX4at7asA/tUwQqExKsIUdH7N4LEvs0m2SJcoh777777')


def test_cmd_style():
    """
    Test format of output for CMD.EXE
    """
    output = StringIO()
    output_creds('cmd', 'us-east-1', mockcreds, stream=output)
    actual_output = output.getvalue()
    assert 'set AWS_DEFAULT_REGION' in actual_output
    assert 'set AWS_ACCESS_KEY_ID' in actual_output
    assert 'set AWS_SECRET_ACCESS_KEY' in actual_output
    assert 'set AWS_SESSION_TOKEN' in actual_output


def test_bash_style():
    """
    Test format of output for bash
    """
    output = StringIO()
    output_creds('bash', 'us-east-1', mockcreds, stream=output)
    actual_output = output.getvalue()
    assert 'export AWS_DEFAULT_REGION' in actual_output
    assert 'export AWS_ACCESS_KEY_ID' in actual_output
    assert 'export AWS_SECRET_ACCESS_KEY' in actual_output
    assert 'export AWS_SESSION_TOKEN' in actual_output


@restore_env
def test_autostyle_cmd():
    """
    Remove SHELL from os.environ and make sure that output is for CMD.EXE
    """
    if 'SHELL' in os.environ:
        os.environ.pop('SHELL')
    output = StringIO()
    output_creds(None, 'us-east-1', mockcreds, stream=output)
    actual_output = output.getvalue()
    assert 'set AWS_DEFAULT_REGION' in actual_output
    assert 'set AWS_ACCESS_KEY_ID' in actual_output
    assert 'set AWS_SECRET_ACCESS_KEY' in actual_output
    assert 'set AWS_SESSION_TOKEN' in actual_output


@restore_env
def test_autostyle_shell():
    """
    Mask SHELL so that it is /usr/bin/whatsit/bash and make sure output is for bash
    """
    os.environ['SHELL'] = '/bin/false'
    output = StringIO()
    output_creds(None, 'us-east-1', mockcreds, stream=output)
    actual_output = output.getvalue()
    assert 'export AWS_DEFAULT_REGION' in actual_output
    assert 'export AWS_ACCESS_KEY_ID' in actual_output
    assert 'export AWS_SECRET_ACCESS_KEY' in actual_output
    assert 'export AWS_SESSION_TOKEN' in actual_output


def test_output_roles():
    mockroles = [('a', 'arole'), ('b', 'brole')]
    output = StringIO()
    output_roles(mockroles, stream=output)
    role_lines = output.getvalue().split('\n')
    assert len(role_lines) == 5
    assert 'arole' in role_lines[2]
    assert 'brole' in role_lines[3]
