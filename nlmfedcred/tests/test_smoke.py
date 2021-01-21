import sys
from importlib import import_module


def test_nlmfedcred():
    syms = dir(import_module('nlmfedcred.fedcred'))
    assert 'get_saml_assertion' in syms
    assert 'get_filtered_role_pairs' in syms
    assert 'assume_role_with_saml' in syms
    if sys.platform == 'win32':
        assert 'get_saml_assertion_piv' in syms


def test_cli():
    syms = dir(import_module('nlmfedcred.cli'))
    assert 'main' in syms


def test_idp():
    syms = dir(import_module('nlmfedcred.idp'))
    assert 'IDP' in syms
    assert 'make_idp' in syms


def test_config():
    syms = dir(import_module('nlmfedcred.config'))
    assert 'parse_config' in syms
    assert 'Config' in syms


def test_exceptions():
    syms = dir(import_module('nlmfedcred.exceptions'))
    assert len(syms) > 0


def test_martcard():
    syms = dir(import_module('nlmfedcred.smartcard'))
    assert 'main' in syms
