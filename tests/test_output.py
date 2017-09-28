"""
Test that the output based on a set of credentials is correct.
"""
import pytest


@pytest.mark.skip(reason='Not yet implemented')
def test_cmd_style():
    """
    Test format of output for CMD.EXE
    """
    assert False


@pytest.mark.skip(reason='Not yet implemented')
def test_bash_style():
    """
    Test format of output for bash
    """
    assert False


@pytest.mark.skip(reason='Not yet implemented')
def test_autostyle_cmd():
    """
    Remove SHELL from os.environ and make sure that output is for CMD.EXE
    """
    assert False


@pytest.mark.skip(reason='Not yet implemented')
def test_autostyle_shell():
    """
    Mask SHELL so that it is /usr/bin/whatsit/bash and make sure output is for bash
    """
    assert False
