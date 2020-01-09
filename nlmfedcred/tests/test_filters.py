"""
Test that filtering functions find correct principals and roles
"""
from base64 import b64decode
from datetime import datetime

import pytest
from nlmfedcred import fedcred


def test_data_decodes(samldata):
    samlxml = b64decode(samldata).decode('utf-8')
    assert samlxml.startswith('<Response xmlns=')


def test_get_deadline(samldata):
    deadline = fedcred.get_deadline(samldata)
    assert isinstance(deadline, datetime)
    assert deadline.second == 17


def test_longest_duration_past(samldata):
    with pytest.raises(ValueError):
        fedcred.get_longest_duration(samldata)


def test_longest_duration_ok(samldata):
    fake_now = datetime.strptime('2017-09-29T10:48:16Z', '%Y-%m-%dT%H:%M:%SZ')
    duration = fedcred.get_longest_duration(samldata, fake_now)
    assert duration == 13801


def test_finds_all_roles(samldata):
    rolepairs = fedcred.get_role_pairs(samldata)
    assert isinstance(rolepairs, list)
    assert len(rolepairs) == 6
    for pair in rolepairs:
        assert isinstance(pair, tuple)
        assert len(pair) == 2


def test_finds_all_roles_in_wg(samldata_wg):
    rolepairs = fedcred.get_role_pairs(samldata_wg)
    assert isinstance(rolepairs, list)
    assert len(rolepairs) == 7
    for pair in rolepairs:
        assert isinstance(pair, tuple)
        assert len(pair) == 2


def test_filter_on_missing_account(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, account='77')
    assert len(rolepairs) == 0


def test_filter_on_account(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, account='070163433501')
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


def test_filter_on_account_role_exact(samldata_sysop):
    rolepairs = fedcred.get_filtered_role_pairs(samldata_sysop, account='626642342379', name='nlm_aws_sysops')
    assert len(rolepairs) == 1
    role = rolepairs[0][1]
    assert role.endswith(':role/nlm_aws_sysops')


def test_filter_on_role_without_prefix(samldata_sysop):
    rolepairs = fedcred.get_filtered_role_pairs(samldata_sysop, name='sysops_super')
    assert len(rolepairs) == 1
    role = rolepairs[0][1]
    assert role.endswith(':role/nlm_aws_sysops_super')


def test_filter_on_account_role(samldata):
    rolepairs = fedcred.get_filtered_role_pairs(samldata, account='070163433501', name='nlm_aws_admins')
    assert len(rolepairs) == 1
    role = rolepairs[0][1]
    assert role == 'arn:aws:iam::070163433501:role/nlm_aws_admins'
