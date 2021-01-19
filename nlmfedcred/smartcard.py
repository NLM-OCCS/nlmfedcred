#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from PyKCS11 import (
    PyKCS11Lib,
    CKA_CLASS, CKA_VALUE, CKA_ID,
    CKF_SERIAL_SESSION, CKF_RW_SESSION,
    CKO_CERTIFICATE
)


def find_pkcs11_library(raw_path=None):
    if not raw_path:
        if sys.platform == 'win32':
            raw_path = r'C:\Program Files\HID Global\ActivClient'
        else:
            raw_path = r'/Library/OpenSC/lib'
    path = Path(raw_path)
    if path.exists() and path.is_dir():
        if sys.platform == 'win32':
            path = path.joinpath('acpkcs211.dll')
        else:
            path = path.joinpath('opensc-pkcs11.so')
    if not path.exists():
        raise ValueError('{}: file not found'.format(str(path)))
    return str(path)


def read_certs(pin, path):
    pkcs11 = PyKCS11Lib()
    pkcs11.load(path)
    slot = pkcs11.getSlotList(tokenPresent=False)[0]
    session = pkcs11.openSession(slot, CKF_SERIAL_SESSION | CKF_RW_SESSION)

    # Here is where I enter the PIV code:
    session.login(pin)

    # Now enumerate the certificates and convert
    certs = session.findObjects([(CKA_CLASS, CKO_CERTIFICATE)])
    result = []
    for cert in certs:
        cka_value, cka_id = session.getAttributeValue(cert, [CKA_VALUE, CKA_ID])
        cert_der = bytes(cka_value)
        cert = x509.load_der_x509_certificate(cert_der, default_backend())
        result.append(cert)
    return result


def read_certs_command(opts):
    path = find_pkcs11_library(opts.lib)
    pin = opts.pin
    certs = read_certs(pin, path)

    for i, cert in enumerate(certs):
        print('Certificate {}:'.format(i))
        print('  Valid from {} to {}'.format(
            cert.not_valid_before.strftime('%Y-%m-%d'),
            cert.not_valid_after.strftime('%Y-%m-%d'),
        ))
        issuers = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        if len(issuers) > 0:
            print('  Issuer: {}'.format(issuers[0].value))
        subjects = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if len(subjects) > 0:
            print('  Subject: {}'.format(subjects[0].value))
        print('')


def get_public_key(pin, path, cert_num):
    certs = read_certs(pin, path)

    if cert_num < 0:
        print('error: certificate should be non-negative', file=sys.stderr)
        return
    elif cert_num >= len(certs):
        print('error: no such certificate', file=sys.stderr)
        return
    cert = certs[cert_num]
    return cert.public_key()


def make_openssh_command(opts):
    pubkey = get_public_key(opts.pin, find_pkcs11_library(opts.lib), opts.cert)
    pubbytes = pubkey.public_bytes(
        encoding=Encoding.OpenSSH,
        format=PublicFormat.OpenSSH,
    )
    pubbytes = pubbytes.decode('utf-8')
    print(pubbytes + ' ' + os.getlogin() + '-piv')


def make_pem_command(opts):
    pubkey = get_public_key(opts.pin, find_pkcs11_library(opts.lib), opts.cert)
    pubbytes = pubkey.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )
    pubbytes = pubbytes.decode('utf-8')
    print(pubbytes, end='')


def create_parser(prog_name):
    parser = argparse.ArgumentParser(prog=prog_name, description='SmartCard proof of concept')
    sp = parser.add_subparsers(title='commands', dest='command', help='Enter a command to run')

    readcerts = sp.add_parser('certs', help='Reads certficates from your smart card')
    readcerts.set_defaults(func=read_certs_command)
    readcerts.add_argument('pin', metavar='PIN',
                           help='You must enter your smart card PIN on the CLI, for now')
    readcerts.add_argument('--lib', metavar='PATH', default=None,
                           help='Specify the path of the PKCS 11 library to load')

    openssh = sp.add_parser('openssh', help='Read authentication certificate and write an OpenSSH file')
    openssh.set_defaults(func=make_openssh_command)
    openssh.add_argument('pin', metavar='PIN',
                         help='You must enter your smart card PIN on the CLI, for now')
    openssh.add_argument('--cert', metavar='NUMBER', default=0, type=int,
                         help='Which certificate')
    openssh.add_argument('--key', metavar='PATH', default=None,
                         help='Path to save the OpenSSH key')
    openssh.add_argument('--lib', metavar='PATH', default=None,
                         help='Specify the path of the PKCS 11 library to load')

    makepem = sp.add_parser('pem', help='Read authentication certificate and write a PEM file')
    makepem.set_defaults(func=make_pem_command)
    makepem.add_argument('pin', metavar='PIN',
                         help='You must enter your smart card PIN on the CLI, for now')
    makepem.add_argument('--cert', metavar='NUMBER', default=0, type=int,
                         help='Which certificate')
    makepem.add_argument('--key', metavar='PATH', default=None,
                         help='Path to save the OpenSSH key')
    makepem.add_argument('--lib', metavar='PATH', default=None,
                         help='Specify the path of the PKCS 11 library to load')
    return parser


def main():
    parser = create_parser(sys.argv[0])
    opts = parser.parse_args(sys.argv[1:])
    if not hasattr(opts, 'func'):
        sys.stderr.write('Please enter a command...\n')
        parser.print_help(file=sys.stderr)
        return
    opts.func(opts)


if __name__ == '__main__':
    main()
