import ctypes
from ctypes import POINTER
from ctypes import wintypes as wt
from ctypes.util import find_library


HCERTSTORE = POINTER(wt.ULONG)

# Certificate Encoding Types

# Certificate and Message encoding types
#
# The encoding type is a DWORD containing both the certificate and message
# encoding types. The certificate encoding type is stored in the LOWORD.
# The message encoding type is stored in the HIWORD. Some functions or
# structure fields require only one of the encoding types. The following
# naming convention is used to indicate which encoding type(s) are
# required:
#      dwEncodingType (both encoding types are required)
#      dwMsgAndCertEncodingType (both encoding types are required)
#      dwMsgEncodingType (only msg encoding type is required)
#      dwCertEncodingType (only cert encoding type is required)
#
# Its always acceptable to specify both.
CERT_ENCODING_TYPE_MASK     = 0x0000FFFF
CMSG_ENCODING_TYPE_MASK     = 0xFFFF0000


CRYPT_ASN_ENCODING          = 0x00000001
CRYPT_NDR_ENCODING          = 0x00000002
X509_ASN_ENCODING           = 0x00000001
X509_NDR_ENCODING           = 0x00000002
PKCS_7_ASN_ENCODING         = 0x00010000
PKCS_7_NDR_ENCODING         = 0x00020000


def get_cert_encoding_type(x):
    return (x & CERT_ENCODING_TYPE_MASK)


def get_cmsg_encoding_type(x):
    return (x & CMSG_ENCODING_TYPE_MASK)


CERT_V1     = 0
CERT_V2     = 1
CERT_V3     = 2

# Certificate Information Flags
CERT_INFO_VERSION_FLAG                      = 1
CERT_INFO_SERIAL_NUMBER_FLAG                = 2
CERT_INFO_SIGNATURE_ALGORITHM_FLAG          = 3
CERT_INFO_ISSUER_FLAG                       = 4
CERT_INFO_NOT_BEFORE_FLAG                   = 5
CERT_INFO_NOT_AFTER_FLAG                    = 6
CERT_INFO_SUBJECT_FLAG                      = 7
CERT_INFO_SUBJECT_PUBLIC_KEY_INFO_FLAG      = 8
CERT_INFO_ISSUER_UNIQUE_ID_FLAG             = 9
CERT_INFO_SUBJECT_UNIQUE_ID_FLAG            = 10
CERT_INFO_EXTENSION_FLAG                    = 11

# Certificate Find Types
CERT_COMPARE_MASK           = 0xFFFF
CERT_COMPARE_SHIFT          = 16
CERT_COMPARE_ANY            = 0
CERT_COMPARE_SHA1_HASH      = 1
CERT_COMPARE_NAME           = 2
CERT_COMPARE_ATTR           = 3
CERT_COMPARE_MD5_HASH       = 4
CERT_COMPARE_PROPERTY       = 5
CERT_COMPARE_PUBLIC_KEY     = 6
CERT_COMPARE_HASH           = CERT_COMPARE_SHA1_HASH
CERT_COMPARE_NAME_STR_A     = 7
CERT_COMPARE_NAME_STR_W     = 8
CERT_COMPARE_KEY_SPEC       = 9
CERT_COMPARE_ENHKEY_USAGE   = 10
CERT_COMPARE_CTL_USAGE      = CERT_COMPARE_ENHKEY_USAGE
CERT_COMPARE_SUBJECT_CERT   = 11
CERT_COMPARE_ISSUER_OF      = 12
CERT_COMPARE_EXISTING       = 13
CERT_COMPARE_SIGNATURE_HASH = 14
CERT_COMPARE_KEY_IDENTIFIER = 15
CERT_COMPARE_CERT_ID        = 16
CERT_COMPARE_CROSS_CERT_DIST_POINTS = 17

CERT_COMPARE_PUBKEY_MD5_HASH = 18

CERT_COMPARE_SUBJECT_INFO_ACCESS = 19
CERT_COMPARE_HASH_STR       = 20
CERT_COMPARE_HAS_PRIVATE_KEY = 21

CERT_FIND_ANY           = (CERT_COMPARE_ANY << CERT_COMPARE_SHIFT)
CERT_FIND_SHA1_HASH     = (CERT_COMPARE_SHA1_HASH << CERT_COMPARE_SHIFT)
CERT_FIND_MD5_HASH      = (CERT_COMPARE_MD5_HASH << CERT_COMPARE_SHIFT)
CERT_FIND_SIGNATURE_HASH = (CERT_COMPARE_SIGNATURE_HASH << CERT_COMPARE_SHIFT)
CERT_FIND_KEY_IDENTIFIER = (CERT_COMPARE_KEY_IDENTIFIER << CERT_COMPARE_SHIFT)
CERT_FIND_HASH          = CERT_FIND_SHA1_HASH
CERT_FIND_PROPERTY      = (CERT_COMPARE_PROPERTY << CERT_COMPARE_SHIFT)
CERT_FIND_PUBLIC_KEY    = (CERT_COMPARE_PUBLIC_KEY << CERT_COMPARE_SHIFT)
CERT_FIND_SUBJECT_NAME  = (CERT_COMPARE_NAME << CERT_COMPARE_SHIFT | CERT_INFO_SUBJECT_FLAG)
CERT_FIND_SUBJECT_ATTR  = (CERT_COMPARE_ATTR << CERT_COMPARE_SHIFT | CERT_INFO_SUBJECT_FLAG)
CERT_FIND_ISSUER_NAME   = (CERT_COMPARE_NAME << CERT_COMPARE_SHIFT | CERT_INFO_ISSUER_FLAG)
CERT_FIND_ISSUER_ATTR   = (CERT_COMPARE_ATTR << CERT_COMPARE_SHIFT | CERT_INFO_ISSUER_FLAG)
CERT_FIND_SUBJECT_STR_A = (CERT_COMPARE_NAME_STR_A << CERT_COMPARE_SHIFT | CERT_INFO_SUBJECT_FLAG)
CERT_FIND_SUBJECT_STR_W = (CERT_COMPARE_NAME_STR_W << CERT_COMPARE_SHIFT | CERT_INFO_SUBJECT_FLAG)
CERT_FIND_SUBJECT_STR   = CERT_FIND_SUBJECT_STR_W
CERT_FIND_ISSUER_STR_A  = (CERT_COMPARE_NAME_STR_A << CERT_COMPARE_SHIFT | CERT_INFO_ISSUER_FLAG)
CERT_FIND_ISSUER_STR_W  = (CERT_COMPARE_NAME_STR_W << CERT_COMPARE_SHIFT | CERT_INFO_ISSUER_FLAG)
CERT_FIND_ISSUER_STR    = CERT_FIND_ISSUER_STR_W
CERT_FIND_KEY_SPEC      = (CERT_COMPARE_KEY_SPEC << CERT_COMPARE_SHIFT)
CERT_FIND_ENHKEY_USAGE  = (CERT_COMPARE_ENHKEY_USAGE << CERT_COMPARE_SHIFT)
CERT_FIND_CTL_USAGE     = CERT_FIND_ENHKEY_USAGE

CERT_FIND_SUBJECT_CERT  = (CERT_COMPARE_SUBJECT_CERT << CERT_COMPARE_SHIFT)
CERT_FIND_ISSUER_OF     = (CERT_COMPARE_ISSUER_OF << CERT_COMPARE_SHIFT)
CERT_FIND_EXISTING      = (CERT_COMPARE_EXISTING << CERT_COMPARE_SHIFT)
CERT_FIND_CERT_ID       = (CERT_COMPARE_CERT_ID << CERT_COMPARE_SHIFT)
CERT_FIND_CROSS_CERT_DIST_POINTS = (CERT_COMPARE_CROSS_CERT_DIST_POINTS << CERT_COMPARE_SHIFT)


CERT_FIND_PUBKEY_MD5_HASH = (CERT_COMPARE_PUBKEY_MD5_HASH << CERT_COMPARE_SHIFT)

CERT_FIND_SUBJECT_INFO_ACCESS = (CERT_COMPARE_SUBJECT_INFO_ACCESS << CERT_COMPARE_SHIFT)

CERT_FIND_HASH_STR      = (CERT_COMPARE_HASH_STR << CERT_COMPARE_SHIFT)
CERT_FIND_HAS_PRIVATE_KEY = (CERT_COMPARE_HAS_PRIVATE_KEY << CERT_COMPARE_SHIFT)


class StoreInfo(ctypes.Structure):
    _fields_ = [
        ('cbSize', wt.DWORD),
    ]


# CRYPT_INTEGER_BLOB
# CRYPT_UINT_BLOB
# CRYPT_OBJID_BLOB
# CERT_NAME_BLOB
# CERT_RDN_VALUE_BLOB
# CERT_BLOB
# CRL_BLOB
# DATA_BLOB
# CRYPT_DATA_BLOB
# CRYPT_HASH_BLOB
# CRYPT_DIGEST_BLOB
# CRYPT_DER_BLOB
# CRYPT_ATTR_BLOB
class CryptDataBlob(ctypes.Structure):
    _fields_ = [
        ('cbData', wt.DWORD),
        ('pbData', wt.PBYTE),
    ]


class CryptBlobArray(ctypes.Structure):
    _fields_ = [
        ('cBlob', wt.DWORD),
        ('rgBlob', POINTER(CryptDataBlob)),
    ]


class CryptBitBlob(ctypes.Structure):
    _fields_ = [
        ('cbData', wt.DWORD),
        ('pbData', wt.PBYTE),
        ('cUnusedBits', wt.DWORD),
    ]


class CryptAlgorithmIdentifier(ctypes.Structure):
    _fields_ = [
        ('pszObjId', wt.LPSTR),
        ('Parameters', CryptDataBlob),
    ]


class CertPublicKeyInfo(ctypes.Structure):
    _fields_ = [
        ('Algorithm', CryptAlgorithmIdentifier),
        ('PublicKey', CryptBitBlob),
    ]


class CertExtension(ctypes.Structure):
    _fields_ = [
        ('pszObjId', wt.LPSTR),
        ('fCritical', wt.BOOL),
        ('Value', CryptDataBlob),
    ]


class CertInfo(ctypes.Structure):
    _fields_ = [
        ('dwVersion', wt.DWORD),
        ('SerialNumber', CryptDataBlob),
        ('SignatureAlgorithm', CryptAlgorithmIdentifier),
        ('Issuer', CryptDataBlob),
        ('NotBefore', wt.FILETIME),
        ('NotAfter', wt.FILETIME),
        ('Subject', CryptDataBlob),
        ('SubjectPublicKeyInfo', CertPublicKeyInfo),
        ('IssuerUniqueId', CryptBitBlob),
        ('SubjectUniqueId', CryptBitBlob),
        ('cExtension', wt.DWORD),
        ('rgExtension', CertExtension),
    ]

class CertContext(ctypes.Structure):
    _fields_ = [
        ('dwCertEncodingType', wt.DWORD),
        ('pbCertEncoded', wt.PBYTE),
        ('cbCertEncoded', wt.DWORD),
        ('pCertInfo', POINTER(CertInfo)),
        ('hCertStore', HCERTSTORE),
    ]


CertEnumSystemStoreCallback = ctypes.WINFUNCTYPE(
    wt.BOOL,
    ctypes.c_void_p,                # pvSystemStore
    wt.DWORD,                       # dwFlags
    POINTER(StoreInfo),             # pStoreInfo
    ctypes.c_void_p,                # pvReserved
    ctypes.c_void_p,                # pvArg
)

PFN_CERT_ENUM_SYSTEM_STORE = POINTER(CertEnumSystemStoreCallback)

CertEnumSystemStore = ctypes.WINFUNCTYPE(
    wt.BOOL,
    wt.DWORD,                       # dwFlags
    ctypes.c_void_p,                # pvSystemStoreLocationPara
    ctypes.c_void_p,                # pvArg
    PFN_CERT_ENUM_SYSTEM_STORE      # pfnEnum (callback function)
)


# see https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-certopenstore
# and https://docs.microsoft.com/en-us/windows/win32/seccrypto/system-store-locations
CertOpenStore = ctypes.WINFUNCTYPE(
    HCERTSTORE,
    wt.LPCSTR,                      # lpszStoreProvider
    wt.DWORD,                       # dwEncodingType
    wt.HANDLE,                      # hCryptProv
    wt.DWORD,                       # dwFlags
    ctypes.c_void_p                 # pvPara
)


CertCloseStore = ctypes.WINFUNCTYPE(
    wt.BOOL,
    HCERTSTORE,                     # hCertStore
    wt.DWORD,                       # dwFlags
)


CertFindCertificateInStore = ctypes.WINFUNCTYPE(
    POINTER(CertContext),
    HCERTSTORE,                     # hCertStore
    wt.DWORD,                       # dwCertEncodingType
    wt.DWORD,                       # dwFindFlags
    wt.DWORD,                       # dwFindType
    ctypes.c_void_p,                # pvFindPara
    POINTER(CertContext),           # pPrevCertContext
)


CertFreeCertificateContext = ctypes.WINFUNCTYPE(
    wt.BOOL,
    POINTER(CertContext),
)

