#!/usr/bin/env python3

from ctypes import (
    LibraryLoader as _LibraryLoader,
    wintypes as _wintypes,
    byref as _byref,
    Structure as _Structure,
    POINTER as _POINTER,
    WinDLL as _WinDLL,
)

from ._console import _Console


class _ConsoleScreenBufferInfo(_Structure):

    _fields_ = [
        ('dwSize', _wintypes._COORD),
        ('dwCursorPosition', _wintypes._COORD),
        ('wAttributes', _wintypes.WORD),
        ('srWindow', _wintypes.SMALL_RECT),
        ('dwMaximumWindowSize', _wintypes._COORD),
    ]

    def __str__(self) -> str:
        return '(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)' % (
            self.dwSize.Y, self.dwSize.X,
            self.dwCursorPosition.Y, self.dwCursorPosition.X,
            self.wAttributes,
            self.srWindow.Top, self.srWindow.Left,
            self.srWindow.Bottom, self.srWindow.Right,
            self.dwMaximumWindowSize.Y, self.dwMaximumWindowSize.X,
        )


_INVALID_HANDLE_VALUE = _wintypes.HANDLE(-1)


_windll = _LibraryLoader(_WinDLL)

_GetStdHandle = _windll.kernel32.GetStdHandle
_GetStdHandle.argtypes = [
    _wintypes.DWORD,
]
_GetStdHandle.restype = _wintypes.HANDLE

_GetConsoleScreenBufferInfo = _windll.kernel32.GetConsoleScreenBufferInfo
_GetConsoleScreenBufferInfo.argtypes = [
    _wintypes.HANDLE,
    _POINTER(_ConsoleScreenBufferInfo),
]
_GetConsoleScreenBufferInfo.restype = _wintypes.BOOL


class Win32Console(_Console):

    def __init__(self) -> None:

        self._handle = _GetStdHandle(-11)
        if self._handle == _INVALID_HANDLE_VALUE.value:
            raise SystemError("GetStdHandle() failed")

        self._buffer_info = _ConsoleScreenBufferInfo()
        self._update_buffer_info()

    def _update_buffer_info(self) -> None:

        if not _GetConsoleScreenBufferInfo(self._handle,
                                           _byref(self._buffer_info)):
            raise SystemError("GetConsoleScreenBufferInfo() failed")

    def print(self, s: str, flush: bool = False) -> None:

        print(s, flush=flush)

    def get_width(self) -> int:

        return self._buffer_info.dwSize.X

    def get_height(self) -> int:

        window = self._buffer_info.srWindow
        return window.Bottom - window.Top + 1

    def get_colors(self) -> int:

        return 16
