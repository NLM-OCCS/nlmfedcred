import argparse
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from PyKCS11 import *


def find_pkcs11_library(raw_path=None):
    if not raw_path:
        if sys.platform == 'win32':
            raw_path = r'C:\Program Files\HID Global\ActivClient'
        else:
            raw_path = r'/Library/Frameworks/ac.ac4mac.pkcs11.framework/Versions/Current/Libraries'
    path = Path(raw_path)
    if path.exists() and path.is_dir():
        if sys.platform == 'win32':
            path = path.joinpath('acpkcs211.dll')
        else:
            path = path.joinpath('acpkcs220.dylib')
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
        print('Certifacte {}:'.format(i))
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


def check_tcl_command(opts):
    import tkinter as tk

    class Application(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master
            self.pack()
            self.create_widgets()

        def create_widgets(self):
            self.hi_there = tk.Button(self)
            self.hi_there["text"] = "Hello World\n(click me)"
            self.hi_there["command"] = self.say_hi
            self.hi_there.pack(side="top")

            self.quit = tk.Button(self, text="QUIT", fg="red",
                                  command=self.master.destroy)
            self.quit.pack(side="bottom")

        def say_hi(self):
            print("hi there, everyone!")

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

def create_parser(prog_name):
    parser = argparse.ArgumentParser(prog=prog_name, description='SmartCard proof of concept')
    sp = parser.add_subparsers(title='commands', dest='command', help='Enter a command to run')

    tclc = sp.add_parser('tcl', help='Validates whether tcl/tk works with your Python installation')
    tclc.set_defaults(func=check_tcl_command)

    readcerts = sp.add_parser('certs', help='Reads certficates from your smart card')
    readcerts.set_defaults(func=read_certs_command)
    readcerts.add_argument('pin', metavar='PIN',
                            help='You must enter your smart card PIN on the CLI, for now')
    readcerts.add_argument('--lib', metavar='PATH', default=None,
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
