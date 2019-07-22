import ctypes
from ctypes.wintypes import *

# From
#    C:/Program Files (x86)/Windows Kits/8.1/Include/um/ncrypt.h
#    C:/Program Files (x86)/Windows Kits/8.1/Include/shared/bcrypt.h

SECURITY_STATUS = LONG

HCRPYTRPROV     = ctypes.POINTER(ULONG)
HCRYPTKEY       = ctypes.POINTER(ULONG)
HCRYPTHASH      = ctypes.POINTER(ULONG)

# Maximum length of Key name, in characters
NCRYPT_MAX_KEY_NAME_LENGTH = 512

# Maximum length of Algorithm name, in characters
NCRYPT_MAX_ALG_ID_LENGTH = 512


# NCRYPT memory management routines for functions that require
# the caller to allocate memory

## TODO: must add arguments
PFN_NCRYPT_ALLOC = ctypes.WINFUNCTYPE(LPVOID, [])
PFN_NCRYPT_FREE = ctypes.WINFUNCTYPE(LPVOID, [])

class NCRYPT_ALLOC_PARA(ctypes.Structure):
    _fields_ = [
        ('cbSize', DWORD),
        ('pfnAlloc', PFN_NCRYPT_ALLOC),
        ('pfnFree', PFN_NCRYPT_FREE),
    ]

# Microsoft built-in providers
MS_KEY_STORAGE_PROVIDER = 'Microsoft Software Key Storage Provider'
MS_SMART_CARD_KEY_STORAGE_PROVIDER = 'Microsoft Smart Card Key Storage Provider'
MS_PLATFORM_KEY_STORAGE_PROVIDER  = 'Microsoft Platform Crypto Provider'

# Common algorithm identifiers

## TODO: dependency on bcrypt here

# Interfaces

## TODO: dependency on bcrypt here

NCRYPT_KEY_STORAGE_INTERFACE            = 0x00010001
NCRYPT_SCHANNEL_INTERFACE               = 0x00010002
NCRYPT_SCHANNEL_SIGNATURE_INTERFACE     = 0x00010003
NCRYPT_KEY_PROTECTION_INTERFACE         = 0x00010004

# Ncrypt generic memory descriptors

NCRYPTBUFFER_VERSION                        = 0

NCRYPTBUFFER_EMPTY                          = 0
NCRYPTBUFFER_DATA                           = 1
NCRYPTBUFFER_PROTECTION_DESCRIPTOR_STRING   = 3
NCRYPTBUFFER_PROTECTION_FLAGS               = 4

NCRYPTBUFFER_SSL_CLIENT_RANDOM              = 20
NCRYPTBUFFER_SSL_SERVER_RANDOM              = 21
NCRYPTBUFFER_SSL_HIGHEST_VERSION            = 22
NCRYPTBUFFER_SSL_CLEAR_KEY                  = 23
NCRYPTBUFFER_SSL_KEY_ARG_DATA               = 24

NCRYPTBUFFER_PKCS_OID                       = 40
NCRYPTBUFFER_PKCS_ALG_OID                   = 41
NCRYPTBUFFER_PKCS_ALG_PARAM                 = 42
NCRYPTBUFFER_PKCS_ALG_ID                    = 43
NCRYPTBUFFER_PKCS_ATTRS                     = 44
NCRYPTBUFFER_PKCS_KEY_NAME                  = 45
NCRYPTBUFFER_PKCS_SECRET                    = 46

NCRYPTBUFFER_CERT_BLOB                      = 47

# NCrypt handles

NCRYPT_HANDLE        = ctypes.POINTER(ULONG)
NCRYPT_PROV_HANDLE   = ctypes.POINTER(ULONG)
NCRYPT_KEY_HANDLE    = ctypes.POINTER(ULONG)
NCRYPT_HASH_HANDLE   = ctypes.POINTER(ULONG)
NCRYPT_SECRET_HANDLE = ctypes.POINTER(ULONG)

# NCrypt API Flags

NCRYPT_NO_PADDING_FLAG                  = 0x00000001
NCRYPT_PAD_PKCS1_FLAG                   = 0x00000002
NCRYPT_PAD_OAEP_FLAG                    = 0x00000004
NCRYPT_PAD_PSS_FLAG                     = 0x00000008
NCRYPT_PAD_CIPHER_FLAG                  = 0x00000010

NCRYPT_REGISTER_NOTIFY_FLAG             = 0x00000001
NCRYPT_UNREGISTER_NOTIFY_FLAG           = 0x00000002
NCRYPT_NO_KEY_VALIDATION                = 0     # TODO: BCRYPT_NO_KEY_VALIDATION
NCRYPT_MACHINE_KEY_FLAG                 = 0x00000020
NCRYPT_SILENT_FLAG                      = 0x00000040
NCRYPT_OVERWRITE_KEY_FLAG               = 0x00000080
NCRYPT_WRITE_KEY_TO_LEGACY_STORE_FLAG   = 0x00000200
NCRYPT_DO_NOT_FINALIZE_FLAG             = 0x00000400
NCRYPT_EXPORT_LEGACY_FLAG               = 0x00000800
NCRYPT_IGNORE_DEVICE_STATE_FLAG         = 0x00001000
NCRYPT_PERSIST_ONLY_FLAG                = 0x40000000
NCRYPT_PERSIST_FLAG                     = 0x80000000

## NCryptOpenStorageProvider

NCRYPT_SILENT_FLAG                      = 0x00000040  # same as CAPI CRYPT_SILENT
NCRYPT_IGNORE_DEVICE_STATE_FLAG         = 0x00001000  # CryptOpenStorageProvider

NCryptOpenStorageProvider = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    ctypes.Pointer(NCRYPT_PROV_HANDLE), # phProvider
    LPWSTR,                             # pszProviderName
    DWORD,                              # dwFlags
)

## NCryptEnumAlgorithms

NCRYPT_CIPHER_OPERATION                 = 0 # TODO: BCRYPT_CIPHER_OPERATION
NCRYPT_HASH_OPERATION                   = 0 # TODO: BCRYPT_HASH_OPERATION
NCRYPT_ASYMMETRIC_ENCRYPTION_OPERATION  = 0 # TODO: BCRYPT_ASYMMETRIC_ENCRYPTION_OPERATION
NCRYPT_SECRET_AGREEMENT_OPERATION       = 0 # TODO: BCRYPT_SECRET_AGREEMENT_OPERATION
NCRYPT_SIGNATURE_OPERATION              = 0 # TODO: BCRYPT_SIGNATURE_OPERATION
NCRYPT_RNG_OPERATION                    = 0 # TODO: BCRYPT_RNG_OPERATION
NCRYPT_KEY_DERIVATION_OPERATION         = 0 # TODO: BCRYPT_KEY_DERIVATION_OPERATION


class NCryptAlgorithms(ctypes.Structure):
    _fields_ = [
        ('pszName', LPWSTR),
        ('dwClass', DWORD),
        ('dwAlgOperations', DWORD),
        ('dwFlags', DWORD),
    ]

PNCryptAlgorithms = ctypes.POINTER(NCryptAlgorithms)


NCryptEnumAlgorithms = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    NCRYPT_PROV_HANDLE,                 # hProvider
    DWORD,                              # dwAlgOperations
    ctypes.POINTER(DWORD),              # pdwAlgCount
    ctypes.POINTER(PNCryptAlgorithms),  # ppAlgList
    DWORD,                              # dwFlags
)

## NCryptIsAlgSupported

NCryptIsAlgSupported = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    NCRYPT_PROV_HANDLE,                 # hProvider
    LPCWSTR,                            # pszAlgId
    DWORD,                              # dwFlags
)

## NCryptEnumKeys

NCRYPT_MACHINE_KEY_FLAG                 = 0x00000020


class NCryptKeyName(ctypes.Structure):
    _fields_ = [
        ('pszName', LPWSTR),
        ('pszAlgId', LPWSTR),
        ('dwLegacyKeySpec', DWORD),
        ('dwFlags', DWORD),
    ]

PNCryptKeyName = ctypes.POINTER(NCryptKeyName)

NCryptEnumKEys = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    NCRYPT_PROV_HANDLE,                 # hProvider
    LPCWSTR,                            # pszScope
    ctypes.POINTER(PNCryptKeyName),     # ppKeyName
    ctypes.POINTER(LPVOID),             # ppEnumState
    DWORD,                              # dwFlags
)

## NCryptEnumStorageProviders

class NCryptProviderName(ctypes.Structure):
    _fields_ = [
        ('pszName', LPWSTR),
        ('pszComment', LPWSTR),
    ]

PNCryptProviderName = ctypes.POINTER(NCryptProviderName)

NCryptEnumStorageProviders = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    ctypes.POINTER(DWORD),              # pdwProviderCount
    ctypes.POINTER(PNCryptProviderName),# ppProviderList
    DWORD,                              # dwFlags
)

## NCryptFreeBuffer

NCryptFreeBuffer = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    LPVOID,                             # pzInput
)


## NCryptOpenKey

NCRYPT_MACHINE_KEY_FLAG                 = 0x00000020
NCRYPT_SILENT_FLAG                      = 0x00000040

NCryptOpenKey = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    NCRYPT_PROV_HANDLE,                 # hProvider
    ctypes.POINTER(NCRYPT_KEY_HANDLE),  # phKey
    LPCWSTR,                            # pszKeyName
    DWORD,                              # dwLegacyKeySpec
    DWORD,                              # dwFlags
)

## NCryptGetProperty and NCryptSetProperty flags
NCRYPT_PERSIST_FLAG                     = 0x80000000
NCRYPT_PERSIST_ONLY_FLAG                = 0x40000000

NCryptGetProperty = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    NCRYPT_HANDLE,                      # hObject
    LPCWSTR,                            # pszProperty
    DWORD,                              # cbOutput
    ctypes.POINTER(DWORD),              # pcbResult
    DWORD,                              # dwFlags
)

NCryptFreeObject = ctypes.WINFUNCTYPE(SECURITY_STATUS,
    NCRYPT_HANDLE,                      # hObject
)
