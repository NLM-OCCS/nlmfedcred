#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import os
import sys
import argparse
from getpass import getpass
from base64 import b64decode
from . import fedcred
from .config import parse_config
from .idp import make_idp, DEFAULT_IDP


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
    parser.add_argument('--profile', '-p', metavar='NAME', default=None,
                        help='Specifies a section of $HOME/.getawscreds to use for your configuration')
    parser.add_argument('--idp', metavar='FQDN', default=None,
                        help='Specify FQDN to use when making federation calls')
    parser.add_argument('--duration', metavar='SECONDS', default=None,
                        help='Specify the duration of the temporary credentials')
    opts = parser.parse_args(args)
    return opts


def output_bash(region, creds, stream=sys.stdout):
    stream.write('export AWS_DEFAULT_REGION="%s"\n' % region)
    stream.write('export AWS_ACCESS_KEY_ID="%s"\n' % creds.access_key)
    stream.write('export AWS_SECRET_ACCESS_KEY="%s"\n' % creds.secret_key)
    stream.write('export AWS_SESSION_TOKEN="%s"\n' % creds.session_token)


def output_cmd(region, creds, stream=sys.stdout):
    stream.write('@echo off\r\n')
    stream.write('set AWS_DEFAULT_REGION=%s\r\n' % region)
    stream.write('set AWS_ACCESS_KEY_ID=%s\r\n' % creds.access_key)
    stream.write('set AWS_SECRET_ACCESS_KEY=%s\r\n' % creds.secret_key)
    stream.write('set AWS_SESSION_TOKEN=%s\r\n' % creds.session_token)


def output_creds(shell, region, creds, stream=sys.stdout):
    if shell is None:
        if 'SHELL' in os.environ:
            shell = 'bash'
        else:
            shell = 'cmd'
    output_func = {'cmd': output_cmd, 'bash': output_bash}[shell]
    output_func(region, creds, stream)


def output_roles(authroles, stream=sys.stdout):
    stream.write('\nAvailable roles below:\n')
    for pair in authroles:
        stream.write('  %s\n' % pair[1])


def execute_from_command_line(args=None):
    fedcred.set_default_creds()

    if args is None:
        args = sys.argv[:]

    opts = parse_args(args[1:])

    config = parse_config(opts.profile, opts.account, opts.role, opts.idp, opts.username)
    if config.idp is None:
        idp = DEFAULT_IDP
    else:
        idp = make_idp(config.idp)

    username = config.username
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

    authroles = fedcred.get_filtered_role_pairs(samlvalue, account=config.account, name=config.role)
    if len(authroles) == 1:
        principal = authroles[0][0]
        role = authroles[0][1]
    elif len(authroles) == 0:
        if opts.account is not None or opts.role is not None:
            authroles = fedcred.get_filtered_role_pairs(samlvalue)
            if len(authroles) == 0:
                sys.stderr.write('No roles found')
            else:
                sys.stderr.write('No roles match your criteria for account and role.\n')
                output_roles(authroles, sys.stderr)
        else:
            sys.stderr.write('No roles found\n')
        sys.exit(1)
    else:
        sys.stderr.write("Multiple potential roles found. Use --account or --role argument to limit to one.\n")
        output_roles(authroles)
        sys.exit(0)

    q = fedcred.assume_role_with_saml(role, principal, samlvalue, opts.region, opts.duration)

    if opts.output:
        os.umask(int('0077', 8))
        stream = open(opts.output, 'w')
    else:
        stream = sys.stdout

    output_creds(opts.shell, opts.region, q.credentials, stream)
