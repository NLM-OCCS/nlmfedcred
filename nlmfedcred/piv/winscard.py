import ctypes
from ctypes import POINTER
from ctypes import wintypes as wt
from ctypes.util import find_library

SCARDCONTEXT = POINTER(wt.ULONG)
SCARDHANDLE = POINTER(wt.ULONG)

SCARD_AUTOALLOCATE = wt.DWORD(-1)
SCARD_SCOPE_USER = wt.DWORD(0x0)                # The context is a user context, and any
SCARD_SCOPE_TERMINAL = wt.DWORD(0x1)            # The context is that of the current terminal,
SCARD_SCOPE_SYSTEM = wt.DWORD(0x2)              # The context is the system context, and any


SCardEstablishContext = ctypes.WINFUNCTYPE(
    wt.LONG,
    wt.DWORD,               # dwScope
    wt.LPCVOID,             # pvReserved1
    wt.LPCVOID,             # pvReserved2
    POINTER(SCARDCONTEXT)   # phContext
)

SCardReleaseContext = ctypes.WINFUNCTYPE(
    wt.LONG,
    SCARDCONTEXT,           # hContext
)

SCardIsValidContext = ctypes.WINFUNCTYPE(
    wt.LONG,
    SCARDCONTEXT            # hContext
)

SCardCancel = ctypes.WINFUNCTYPE(
    wt.LONG,
    SCARDCONTEXT            # hContext
)

# SCARD_ALL_READERS = wt.LPCSTR('SCard$AllReaders')
# SCARD_DEFAULT_READERS = wt.LPCSTR('SCard$DefaultReaders')
# SCARD_LOCAL_READERS = wt.LPCSTR('SCard$LocalReaders')
# SCARD_SYSTEM_READERS = wt.LPCSTR('SCard$SystemReaders')

SCARD_PROVIDER_PRIMARY = wt.DWORD(0x1)          # Primary Provider Id
SCARD_PROVIDER_CSP = wt.DWORD(0x2)              # Crypto Service Provider Id
SCARD_PROVIDER_KSP = wt.DWORD(0x3)              # Key Storage Provider Id

SCARD_STATE_UNAWARE = wt.DWORD(0x00000000)      # The application is unaware of the
SCARD_STATE_IGNORE = wt.DWORD(0x00000001)       # The application requested that
SCARD_STATE_CHANGED = wt.DWORD(0x00000002)      # This implies that there is a
SCARD_STATE_UNKNOWN = wt.DWORD(0x00000004)      # This implies that the given
SCARD_STATE_UNAVAILABLE = wt.DWORD(0x00000008)  # This implies that the actual
SCARD_STATE_EMPTY = wt.DWORD(0x00000010)        # This implies that there is not
SCARD_STATE_PRESENT = wt.DWORD(0x00000020)      # This implies that there is a card
SCARD_STATE_ATRMATCH = wt.DWORD(0x00000040)     # This implies that there is a card
SCARD_STATE_EXCLUSIVE = wt.DWORD(0x00000080)    # This implies that the card in the
SCARD_STATE_INUSE = wt.DWORD(0x00000100)        # This implies that the card in the
SCARD_STATE_MUTE = wt.DWORD(0x00000200)         # This implies that the card in the
SCARD_STATE_UNPOWERED = wt.DWORD(0x00000400)    # This implies that the card in the
SCARD_SHARE_EXCLUSIVE = wt.DWORD(0x1)           # This application is not willing to share this
SCARD_SHARE_SHARED = wt.DWORD(0x2)              # This application is willing to share this
SCARD_SHARE_DIRECT = wt.DWORD(0x3)              # This application demands direct control of
SCARD_LEAVE_CARD = wt.DWORD(0x0)                # Don't do anything special on close
SCARD_RESET_CARD = wt.DWORD(0x1)                # Reset the card on close
SCARD_UNPOWER_CARD = wt.DWORD(0x2)              # Power down the card on close
SCARD_EJECT_CARD = wt.DWORD(0x3)                # Eject the card on close
SC_DLG_MINIMAL_UI = wt.DWORD(0x01)
SC_DLG_NO_UI = wt.DWORD(0x02)
SC_DLG_FORCE_UI = wt.DWORD(0x04)
SCERR_NOCARDNAME = wt.DWORD(0x4000)
SCERR_NOGUIDS = wt.DWORD(0x8000)


class OpencardSearchCriteria(ctypes.Structure):
    _fields_ = [
        ('dwStructSize', wt.DWORD),
        ('lpstrGroupNames', wt.LPWSTR),
        ('nMaxGroupNames', wt.DWORD),
        ('rgguidInterfaces', wt.LPVOID),        # originally LPCGUID - probably a string UUID
        ('cguidInterfaces', wt.DWORD),
        ('lpstrCardNames', wt.LPWSTR),
        ('nMaxCardNames', wt.DWORD),
        ('lpfnCheck', wt.LPVOID),               # callback; must be NULL
        ('lpfnConnect', wt.LPVOID),             # callback; must be NULL
        ('lpfnDisconnect', wt.LPVOID),          # callback; must be NULL
        ('pvUserData', wt.LPVOID),
        ('dwShareMode', wt.DWORD),
        ('dwPreferredProtocols', wt.DWORD),
    ]


class OpencardNameEx(ctypes.Structure):
    _fields_ = [
        ('dwStructSize', wt.DWORD),
        ('hSCardContext', SCARDCONTEXT),
        ('hwndowner', wt.HWND),
        ('dwFlags', wt.DWORD),
        ('lpstrTitle', wt.LPWSTR),
        ('lpstrSearchDesc', wt.LPWSTR),
        ('hIcon', wt.HICON),
        ('pOpenCardSearchCriteria', POINTER(OpencardSearchCriteria)),
        ('lpfnConnect', wt.LPVOID),                 # LPOCNCONNPROCW not copied
        ('pvUserData', wt.LPVOID),
        ('dwShareMode', wt.DWORD),
        ('dwPreferredProtocols', wt.DWORD),
        ('lpstrRdr', wt.LPWSTR),
        ('nMaxRdr', wt.DWORD),
        ('lpstrCard', wt.LPWSTR),
        ('nMaxCard', wt.DWORD),
        ('dwActiveProtocol', wt.DWORD),
        ('hCardHandle', SCARDHANDLE),
    ]


SCardUIDlgSelectCardW = ctypes.WINFUNCTYPE(
    wt.LONG,
    POINTER(OpencardNameEx),
)


SCardGetCardTypeProviderNameW = ctypes.WINFUNCTYPE(
    wt.LONG,
    SCARDCONTEXT,           # hContext
    wt.LPWSTR,              # szCardName
    wt.DWORD,               # dwProviderId
    POINTER(wt.WCHAR),      # szProvider
    wt.LPDWORD,             # pcchProvider
)

SCARD_READER_SEL_AUTH_PACKAGE = wt.DWORD(-629)

SCARD_AUDIT_CHV_FAILURE = wt.DWORD(0x0)         # A smart card holder verification (CHV)
SCARD_AUDIT_CHV_SUCCESS = wt.DWORD(0x1)         # A smart card holder verification (CHV)


class WinSCard:
    def __init__(self):
        winscard_path = find_library('winscard')
        scarddlg_path = find_library('scarddlg')
        self._dll = ctypes.WinDLL(winscard_path)
        self._dlgdll = ctypes.WinDLL(scarddlg_path)
        self.context = wt.PULONG()
        self.context.value = 0
        self._establish_context = SCardEstablishContext(('SCardEstablishContext', self._dll))
        self._release_context = SCardReleaseContext(('SCardReleaseContext', self._dll))
        self._is_valid_context = SCardIsValidContext(('SCardIsValidContext', self._dll))
        self._cancel = SCardCancel(('SCardCancel', self._dll))
        self._select_card = SCardUIDlgSelectCardW(('SCardUIDlgSelectCardW', self._dlgdll))
        self._provider_name = SCardGetCardTypeProviderNameW(('SCardGetCardTypeProviderNameW', self._dll))

    def __enter__(self):
        self.establish_context()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def establish_context(self, scope=SCARD_SCOPE_USER):
        return self._establish_context(scope, 0, 0, ctypes.byref(self.context))

    def open(self, scope=SCARD_SCOPE_USER):
        return self.establish_context(scope)

    def is_valid_context(self):
        return self._is_valid_context(self.context)

    def release_context(self):
        retval = self._release_context(self.context)
        self.context.value = 0
        return retval

    def cancel(self):
        return self._cancel(self.context)

    def close(self):
        self.cancel()
        return self.release_context()

    def open_dialog(self, title='My Select Card Title', flags=SC_DLG_MINIMAL_UI):
        szReader = ctypes.create_unicode_buffer('',256)
        szCard = ctypes.create_unicode_buffer('',256)
        titlebuf = ctypes.create_unicode_buffer(title)
        dlgstruct = OpencardNameEx()

        dlgstruct.dwStructSize = ctypes.sizeof(dlgstruct)
        dlgstruct.hSCardContext = self.context
        dlgstruct.dwFlags = flags
        dlgstruct.lpstrRdr = ctypes.cast(szReader, wt.LPWSTR)
        dlgstruct.nMaxRdr = 256
        dlgstruct.lpstrCard = ctypes.cast(szCard, wt.LPWSTR)
        dlgstruct.nMaxCard = 256
        dlgstruct.lpstrTitle = ctypes.cast(titlebuf, wt.LPWSTR)

        status = self._select_card(ctypes.byref(dlgstruct))
        return (status, szReader.value, szCard.value)

    def provider_name(self, card):
        card = ctypes.create_unicode_buffer(card)
        providerName = ctypes.create_unicode_buffer(256)
        cchProvider = wt.DWORD(256)

        status = self._provider_name(self.context, card, SCARD_PROVIDER_CSP, providerName, cchProvider)

        return (status, providerName.value, cchProvider.value)
