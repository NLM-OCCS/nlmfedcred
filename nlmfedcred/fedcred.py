#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import logging
import os
import re
import sys
from base64 import b64decode
from collections import namedtuple
from datetime import datetime, timedelta

import boto3
import requests
from bs4 import BeautifulSoup
from lxml import etree

from .config import get_home

Credentials = namedtuple('Credentials', ['access_key', 'secret_key', 'session_token'])


logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    from .fedcred_win32 import *       # noqa


def set_default_creds():
    '''
    Make sure the user has some default credentials so that boto will work.
    '''
    home_path = get_home()
    aws_creds_path = os.path.join(home_path, '.aws', 'credentials')
    if not os.path.exists(aws_creds_path):
        os.environ.setdefault('AWS_ACCESS_KEY_ID', '99999999')
        os.environ.setdefault('AWS_SECRET_ACCESS_KEY', '9999999999999999')


def get_hidden_inputs(session, idp):
    if session is None:
        session = requests.session()
    r = session.get(idp.form_url)
    assert r.ok

    soup = BeautifulSoup(r.content, 'lxml')
    form = soup.find_all('form')[0]

    form_data = {}
    for i in form.find_all('input'):
        if 'name' in i.attrs and 'value' in i.attrs:
            form_data[i.attrs['name']] = i.attrs['value']

    return form_data


def get_saml_assertion(username, password, idp, session=None):
    '''
    Authenticate against the IdP, and get the SAML assertion
    '''
    if session is None:
        session = requests.session()
    form_data = get_hidden_inputs(session, idp)
    form_data['USER'] = username
    form_data['PASSWORD'] = password
    r = session.post(idp.login_url, form_data)

    if not r.ok:
        return r.status_code

    soup = BeautifulSoup(r.content, 'lxml')
    samlinput = soup.find('input')

    assert samlinput
    samlvalue = samlinput.attrs['value']
    return samlvalue


def get_deadline(samlvalue):
    namespaces = {
        'p': 'urn:oasis:names:tc:SAML:2.0:protocol',
        'a': 'urn:oasis:names:tc:SAML:2.0:assertion'
    }
    tree = etree.fromstring(b64decode(samlvalue), etree.XMLParser(resolve_entities=False))
    authorization = tree.xpath('/p:Response/a:Assertion/a:AuthnStatement', namespaces=namespaces)[0]
    deadline = authorization.get('SessionNotOnOrAfter')
    if not deadline:
        raise ValueError('The SAML Credentials have no expiration timestamp')
    return datetime.strptime(deadline, '%Y-%m-%dT%H:%M:%SZ')


def get_longest_duration(samlvalue, now=None):
    if not now:
        now = datetime.utcnow()
    deadline = get_deadline(samlvalue) - timedelta(seconds=600)
    if now >= deadline:
        raise ValueError('The credential is expired or will expire in the next 10 minutes')
    return (deadline - now).seconds


def get_role_pairs(samlvalue):
    namespaces = {
        'p': 'urn:oasis:names:tc:SAML:2.0:protocol',
        'a': 'urn:oasis:names:tc:SAML:2.0:assertion'
    }
    tree = etree.fromstring(b64decode(samlvalue), etree.XMLParser(resolve_entities=False))
    stmt = tree.xpath('/p:Response/a:Assertion/a:AttributeStatement', namespaces=namespaces)[0]
    pairs = []
    for a in stmt.xpath('a:Attribute', namespaces=namespaces):
        if a.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role':
            for value in a.xpath('a:AttributeValue', namespaces=namespaces):
                pair_list = value.text.split(',')
                if len(pair_list) == 2:
                    pairs.append((pair_list[0], pair_list[1]))
                else:
                    logger.warning('%s: saml:AttributeValue should encode a pincipal arn and role arn')
    return pairs


def build_filter_expr(account, name):
    arn_expr = 'arn:aws:iam::{:s}'.format(account if account else '[^:]+')
    if name is not None:
        arn_expr += ':role/(nlm_aws_)?{:s}$'.format(name)
    return arn_expr


def filter_role_pairs(pairs, account=None, name=None):
    if not account and not name:
        logger.debug('No account or role filtering')
        return pairs
    arn_expr = build_filter_expr(account, name)
    logger.debug("Filtering role pairs by '%s'", arn_expr)
    filtered_pairs = []
    for pair in pairs:
        role = pair[1]
        if re.match(arn_expr, role):
            filtered_pairs.append(pair)
        else:
            logger.debug('principal %s, role %s: does not match filter', pair[0], pair[1])
    return filtered_pairs


def get_filtered_role_pairs(samlvalue, account=None, name=None):
    return filter_role_pairs(get_role_pairs(samlvalue), account, name)


def make_creds_from_response(q):
    assert q and 'Credentials' in q
    raw = q['Credentials']
    creds = Credentials(raw['AccessKeyId'], raw['SecretAccessKey'], raw['SessionToken'])
    return creds


def assume_role_with_saml(role_arn, principal_arn, samlvalue, region, duration=None):
    '''
    Use the SAML assertion to assume a role.
    '''
    set_default_creds()
    client = boto3.client(service_name='sts', region_name=region)
    if duration is None:
        duration = 3600

    q = client.assume_role_with_saml(RoleArn=role_arn,
                                     PrincipalArn=principal_arn,
                                     SAMLAssertion=samlvalue,
                                     DurationSeconds=duration)
    return make_creds_from_response(q)
