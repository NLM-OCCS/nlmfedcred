#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import os
import sys
import argparse
from bs4 import BeautifulSoup
from lxml import etree
from base64 import b64decode
from boto import sts
from boto import ec2
import re
import logging
import requests


IDP_FORM_URL = 'https://authtest.nih.gov/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM'
IDP_LOGIN_URL = 'https://authtest.nih.gov/siteminderagent/forms/login.fcc'

logger = logging.getLogger(__name__)


def get_home():
    '''
    Get the home directory of the user in a way that should work in Linux, OS X, and Windows
    '''
    if 'HOME' in os.environ:
        home_path = os.environ['HOME']
    elif 'HOMEDRIVE' in os.environ and 'HOMEPATH' in os.environ:
        home_path = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    else:
        home_path = None
    return home_path


def get_user():
    '''
    Get the current username in a way that should work in Linux, OS X, and Windows
    '''
    if 'USER' in os.environ:
        # shell in Linux/OS X
        username = os.environ['USER']
    elif 'USERNAME' in os.environ:
        # shell in Windows
        username = os.environ['USERNAME']
    else:
        # crontab in Linux/OS X, may not work with setuid/setgid programs.
        # We assume a login shell changes semantics; this is by design
        username = os.getlogin()
    return username


def set_default_creds():
    '''
    Make sure the user has some default credentials so that boto will work.
    '''
    home_path = get_home()
    aws_creds_path = os.path.join(home_path, '.aws', 'credentials')
    if not os.path.exists(aws_creds_path):
        os.environ.setdefault('AWS_ACCESS_KEY_ID', '99999999')
        os.environ.setdefault('AWS_SECRET_ACCESS_KEY', '9999999999999999')


def get_hidden_inputs(session):
    if session is None:
        session = requests.session()
    r = session.get(IDP_FORM_URL)
    assert r.ok

    soup = BeautifulSoup(r.content, 'lxml')
    form = soup.find_all('form')[0]

    form_data = {}
    for i in form.find_all('input'):
        if 'name' in i.attrs and 'value' in i.attrs:
            form_data[i.attrs['name']] = i.attrs['value']

    return form_data


def get_saml_assertion(username, password, session=None):
    '''
    Authenticate against the IdP, and get the SAML assertion
    '''
    if session is None:
        session = requests.session()

    form_data = get_hidden_inputs(session)
    form_data['USER'] = username
    form_data['PASSWORD'] = password
    r = session.post(IDP_LOGIN_URL, form_data)

    if not r.ok:
        return r.status_code

    soup = BeautifulSoup(r.content, 'lxml')
    samlinput = soup.find('input')

    assert samlinput
    samlvalue = samlinput.attrs['value']
    return samlvalue


def get_role_pairs(samlvalue):
    namespaces = {
        'p': 'urn:oasis:names:tc:SAML:2.0:protocol',
        'a': 'urn:oasis:names:tc:SAML:2.0:assertion'
    }
    tree = etree.fromstring(b64decode(samlvalue))
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


def filter_role_pairs(pairs, account=None, name=None):
    arn_expr = ''
    if account is not None:
        arn_expr += 'arn:aws:iam::%s' % str(account)
    if name is not None:
        arn_expr += ':role/%s' % str(name)

    if len(arn_expr) == 0:
        logger.debug('No account or role filtering')
        filtered_pairs = pairs
    else:
        logger.debug("Filtering role pairs by '%s'" % arn_expr)
        filtered_pairs = []
        for pair in pairs:
            role = pair[1]
            if re.search(arn_expr, role) is not None:
                filtered_pairs.append(pair)
            else:
                logger.debug('principal %s, role %s: does not match filter' % (pair[0], pair[1]))
    return filtered_pairs


def get_filtered_role_pairs(samlvalue, account=None, name=None):
    return filter_role_pairs(get_role_pairs(samlvalue), account, name)


def assume_role_with_saml(role_arn, principal_arn, samlvalue, region, duration=None):
    '''
    Use the SAML assertion to assume a role.
    '''
    set_default_creds()
    sts_conn = sts.connect_to_region(region)

    if duration is None:
        duration = 3600

    q = sts_conn.assume_role_with_saml(role_arn=role_arn,
                                       principal_arn=principal_arn,
                                       saml_assertion=samlvalue,
                                       duration_seconds=duration)
    assert q
    return q
