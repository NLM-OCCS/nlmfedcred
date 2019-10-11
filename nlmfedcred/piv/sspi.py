import ctypes
from ctypes import POINTER
from ctypes import wintypes as wt


# https://docs.microsoft.com/en-us/windows/win32/api/sspi/ns-sspi-secbuffer
class SecBuffer(ctypes.Structure):
    _fields_ = [
        ('cbBuffer', ctypes.c_ulong),
        ('BufferType', ctypes.c_ulong),
        ('pvBuffer', ctypes.c_char_p),
    ]


# https://docs.microsoft.com/en-us/windows/win32/api/sspi/ns-sspi-secbufferdesc
class SecBufferDesc(ctypes.Structure):
    _fields_ = [
        ('ulVersion', ctypes.c_ulong),
        ('cBuffers', ctypes.c_ulong),
        ('pBuffers', POINTER(SecBuffer)),
    ]


PSecBuffer = POINTER(SecBuffer)
PSecBufferDesc = POINTER(SecBufferDesc)


# https://docs.microsoft.com/en-us/windows/win32/api/sspi/ns-sspi-secpkginfoa
class SecPkgInfo(ctypes.Structure):
    _fields_ = [
        ('fCapabilities', ctypes.c_ulong),
        ('wVersion', ctypes.c_ushort),
        ('wRPCID', ctypes.c_ushort),
        ('cbMaxToken', ctypes.c_ulong),
        ('Name', wt.LPSTR),
        ('Comment', wt.LPSTR),
    ]


PSecPkgInfo = POINTER(SecPkgInfo)


# https://docs.microsoft.com/en-us/windows/win32/api/sspi/ns-sspi-securityfunctiontablea
class SecurityFunctionTable(ctypes.Structure):
    # LATER
    pass


InitSecurityInterface = ctypes.WINFUNCTYPE(
    POINTER(SecurityFunctionTable),
)

# https://docs.microsoft.com/en-us/windows/win32/secauthn/authentication-functions#functions-implemented-by-user-mode-sspaps


EnumerateSecurityPackages = ctypes.WINFUNCTYPE(
    wt.LONG,
    POINTER(ctypes.c_ulong),            # pcPackages
    POINTER(PSecPkgInfo),               # ppPackageInfo
)
