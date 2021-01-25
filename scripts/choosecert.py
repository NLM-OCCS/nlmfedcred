import sys
from argparse import ArgumentParser

import win32api
import win32con

# Places where there actually are certificates:
#
# HKEY_CURRENT_USER\Software\Microsoft\SystemCertificates\CA\Certificates
# HKEY_CURRENT_USER\Software\Microsoft\SystemCertificates\ADDRESSBOOK\Certificates
#
# Windows says Oid 2.16.840.1.101.3.2.1.3.13 proves my identity to a foreign computer
# Windows says Oids 1.3.6.1.5.2.3.4 and 1.3.6.1.5.5.7.3.17 mean smart card
# These are all under "Enhanced Key Usage" extension, so, we use:
#   - cryptography.x509.oid.ExtendedKeyUsageOID,
#   https://cryptography.io/en/latest/x509/reference/#cryptography.x509.oid.ExtendedKeyUsageOID
#
# And we iterate to find those that are used for
#   - CLIENT_AUTH
# And are still valid

NAME_TO_HANDLE = {
    'HKCU': win32con.HKEY_CURRENT_USER,
    'HKLM': win32con.HKEY_LOCAL_MACHINE
}

MY_THUMBPRINT = '62C42389B2B60632733FBD6665E332EEB7945151'
DEFAULT_STORE_PATH = 'Software\\Microsoft\\SystemCertificates'


def hkey2handle(hKey):
    if hKey is None:
        return win32con.HKEY_CURRENT_USER
    if isinstance(hKey, str):
        return NAME_TO_HANDLE[hKey.upper()]
    return hKey


def hkey2name(hKey):
    if hKey is None or hKey == win32con.HKEY_CURRENT_USER:
        return 'HKCU:'
    if hKey == win32con.HKEY_LOCAL_MACHINE:
        return 'HKLM:'
    return ''


def create_parser(prog_name):
    parser = ArgumentParser(prog=prog_name, description='Extract information from certificates in the registry')
    return parser


def store_certificate_keys(path, hKey=win32con.HKEY_LOCAL_MACHINE):
    hKey = hkey2handle(hKey)
    k = win32api.RegOpenKey(hKey, path)
    nsubkeys, nvalues, nanos = win32api.RegQueryInfoKey(k)
    subkeys = [win32api.RegEnumKey(k, i) for i in range(nsubkeys)]
    win32api.RegCloseKey(k)
    return subkeys


def store_certficate_value(hKey, cert_name):
    k = win32api.RegOpenKey(hKey, cert_name)
    value, dummy = win32api.RegQueryValueEx(k, 'Blob')
    win32api.RegCloseKey(k)
    return value


def _is_thumbprint(key):
    HEXDIGITS = '0123456789ABCDEF'
    return len(key)==40 and all(c in HEXDIGITS for c in key)


def _search_guts(results, hKey, path, parent=''):
    k = win32api.RegOpenKey(hKey, path)
    try:
        nsubkeys, nvalues, nanos = win32api.RegQueryInfoKey(k)
        for i in range(nsubkeys):
            subkey = win32api.RegEnumKey(k, i)
            if _is_thumbprint(subkey):
                results.append(parent + subkey)
            else:
                _search_guts(results, k, subkey, parent=parent + path + '\\')
    finally:
        win32api.RegCloseKey(k)


def store_search(path, hKey=win32con.HKEY_CURRENT_USER):
    """
    Recurse through the registry to find certificates with particular value
    """
    hKey = hkey2handle(hKey)
    results = []
    _search_guts(results, hKey, path, parent=hkey2name(hKey))
    return results


def store_certificates(path, hKey=win32con.HKEY_CURRENT_USER):
    hKey = hkey2handle(hKey)
    k = win32api.RegOpenKey(hKey, path)
    nsubkeys, nvalues, nanos = win32api.RegQueryInfoKey(k)
    subkeys = [win32api.RegEnumKey(k, i) for i in range(nsubkeys)]
    certificates = dict(
        (name, store_certficate_value(k, name))
        for name in subkeys
    )
    win32api.RegCloseKey(k)
    return certificates


def main():
    parser = create_parser(sys.argv[0])
    opts = parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    main()
