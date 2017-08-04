from importlib import import_module


def test_nlmfedcred():
    syms = dir(import_module('nlmfedcred.fedcred'))
    assert 'get_saml_assertion' in syms
    assert 'get_filtered_role_pairs' in syms
    assert 'assume_role_with_saml' in syms


def test_cli():
    syms = dir(import_module('nlmfedcred.cli'))
    assert 'execute_from_command_line' in syms
