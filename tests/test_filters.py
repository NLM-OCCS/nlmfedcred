"""
Test that filtering functions find correct principals and roles
"""
import os
import pytest
from nlmfedcred import fedcred
from base64 import b64decode

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='module')
def samldata():
    samlout_path = os.path.join(DATA_DIR, 'samlout.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()


@pytest.fixture(scope='module')
def samldatawg():
    samlout_path = os.path.join(DATA_DIR, 'samlout-wg.b64')
    with open(samlout_path, 'rb') as f:
        return f.read()


def test_data_decodes(samldata):
    samlxml = b64decode(samldata).decode('utf-8')
    assert type(samlxml) == str
    assert samlxml.startswith('<Response xmlns=')


def test_finds_all_roles(samldata):
    rolepairs = fedcred.get_role_pairs(samldata)
    assert isinstance(rolepairs, list)
    assert len(rolepairs) == 6
    for pair in rolepairs:
        assert isinstance(pair, tuple)
        assert len(pair) == 2


def test_finds_all_roles_in_wg(samldatawg):
    rolepairs = fedcred.get_role_pairs(samldatawg)
    assert isinstance(rolepairs, list)
    assert len(rolepairs) == 7
    for pair in rolepairs:
        assert isinstance(pair, tuple)
        assert len(pair) == 2


def test_filter_on_missing_account(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, account=77)
    assert len(rolepairs) == 0


def test_filter_on_account(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, account=70163433501)
    assert len(rolepairs) == 3
    justroles = [p[1] for p in rolepairs]
    assert 'arn:aws:iam::070163433501:role/nlm_aws_admins' in justroles
    for role in justroles:
        assert role.startswith('arn:aws:iam::070163433501:role/')


def test_filter_on_role(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, name='nlm_aws_admins')
    assert len(rolepairs) == 2
    justroles = [p[1] for p in rolepairs]
    for role in justroles:
        role.endswith(':role/nlm_aws_admins')


def test_filter_on_account_role(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, account=70163433501, name='nlm_aws_admins')
    assert len(rolepairs) == 1
    role = rolepairs[0][1]
    assert role == 'arn:aws:iam::070163433501:role/nlm_aws_admins'
