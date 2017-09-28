#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import os
import sys
import argparse
from getpass import getpass
from base64 import b64decode
import nlmfedcred as fedcred
from nlmfedcred.idp import make_idp, DEFAULT_IDP


def parse_args(args):
    parser = argparse.ArgumentParser(prog="getawscreds", description='Output shell variables for an AWS role')
    parser.add_argument('--username', '-u', metavar='USERNAME', type=str, default=None,
                        help='NIH Active Directory username')
    parser.add_argument('--password', metavar='PASSWORD', default=None,
                        help='You will be prompted to enter a password if none is provided')
    parser.add_argument('--role', '-r', metavar='NAME', default=None,
                        help='Filters possible roles by match')
    parser.add_argument('--region', metavar='REGION', default='us-east-1',
                        help='Specify AWS region (default "us-east-1")')
    parser.add_argument('--output', '-o', metavar='PATH', default=None,
                        help='Path where the output should be written')
    parser.add_argument('--samlout', '-s', metavar='PATH', default=None,
                        help='Debugging utility to save the SAML output')
    parser.add_argument('--shell', metavar='SHELL', default=None, choices=['bash', 'cmd'],
                        help="Choose either bash or cmd style output")
    parser.add_argument('--account', '-a', metavar='ACCOUNT', default=None,
                        help='Account number filters possible roles by account number match')
    parser.add_argument('--idp', metavar='FQDN', default=None,
                        help='Specify FQDN to use when making federation calls')
    parser.add_argument('--duration', metavar='SECONDS', default=None,
                        help='Specify the duration of the temporary credentials')
    opts = parser.parse_args(args)
    return opts


def output_bash(region, creds):
    print('export AWS_DEFAULT_REGION="%s"' % region)
    print('export AWS_ACCESS_KEY_ID="%s"' % creds.access_key)
    print('export AWS_SECRET_ACCESS_KEY="%s"' % creds.secret_key)
    print('export AWS_SESSION_TOKEN="%s"' % creds.session_token)


def output_cmd(region, creds):
    print('@echo off')
    print('set AWS_DEFAULT_REGION=%s' % region)
    print('set AWS_ACCESS_KEY_ID=%s' % creds.access_key)
    print('set AWS_SECRET_ACCESS_KEY=%s' % creds.secret_key)
    print('set AWS_SESSION_TOKEN=%s' % creds.session_token)


def output_creds(shell, region, creds):
    if shell is None:
        if 'SHELL' in os.environ:
            shell = 'bash'
        else:
            shell = 'cmd'
    output_func = {'cmd': output_cmd, 'bash': output_bash}[shell]
    output_func(region, creds)


def execute_from_command_line(args=None):
    fedcred.set_default_creds()

    if args is None:
        args = sys.argv[:]

    opts = parse_args(args[1:])

    if opts.idp is None:
        idp = DEFAULT_IDP
    else:
        idp = make_idp(opts.idp)

    if opts.username is None:
        username = fedcred.get_user()
    else:
        username = opts.username

    if opts.password is not None:
        password = opts.password
    else:
        password = getpass('Enter Password: ')

    samlvalue = fedcred.get_saml_assertion(username, password, idp)
    if samlvalue == 'US-EN':
        sys.stderr.write('No SAML Binding: could it be an invalid password?\n')
        sys.exit(1)

    if opts.samlout is not None:
        xmlvalue = b64decode(samlvalue)
        with open(opts.samlout, 'wb') as f:
            f.write(xmlvalue)
        print('Saml output saved without processing')
        sys.exit(0)

    principal = None
    role = None

    authroles = fedcred.get_filtered_role_pairs(samlvalue, account=opts.account, name=opts.role)
    if len(authroles) == 1:
        principal = authroles[0][0]
        role = authroles[0][1]
    elif len(authroles) == 0:
        if opts.account is not None or opts.role is not None:
            sys.stderr.write('No roles match your criteria for account and role\n')
        else:
            sys.stderr.write('No roles found\n')
        sys.exit(1)
    else:
        while role is None:
            print('')
            for i in range(len(authroles)):
                print('%i. %s' % (i+1, authroles[i][1]))
            print('')
            try:
                i = int(getpass('Choose one of the previous roles: ')) - 1
                if i >= 0 and i < len(authroles):
                    principal = authroles[i][0]
                    role = authroles[i][1]
                else:
                    raise ValueError()
            except ValueError:
                sys.stderr.write("That's not a valid choice\n")
                pass

    q = fedcred.assume_role_with_saml(role, principal, samlvalue, opts.region, opts.duration)

    if opts.output:
        os.umask(int('0077', 8))
        sys.stdout = open(opts.output, 'w')

    output_creds(opts.shell, opts.region, q.credentials)
