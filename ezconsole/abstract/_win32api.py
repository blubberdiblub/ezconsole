#!/usr/bin/env python3

from ctypes import (
    POINTER as _POINTER,
    Structure as _Structure,
    LibraryLoader as _LibraryLoader,
    WinDLL as _WinDLL,
)

from ctypes.wintypes import (
    BOOL,
    DWORD,
    HANDLE,
    LPCWSTR,
    LPDWORD,
    LPVOID,
    LPWSTR,
    PSMALL_RECT,
    SMALL_RECT,
    WCHAR,
    WORD,
    _COORD as COORD,
)


class CharInfo(_Structure):

    _fields_ = [
        ('Char', WCHAR),
        ('Attributes', WORD),
    ]


class ConsoleScreenBufferInfo(_Structure):

    _fields_ = [
        ('dwSize', COORD),
        ('dwCursorPosition', COORD),
        ('wAttributes', WORD),
        ('srWindow', SMALL_RECT),
        ('dwMaximumWindowSize', COORD),
    ]

    def __str__(self) -> str:
        return '<(%d,%d),(%d,%d),%04x,((%d,%d),(%d,%d)),(%d,%d)>' % (
            self.dwSize.Y, self.dwSize.X,
            self.dwCursorPosition.Y, self.dwCursorPosition.X,
            self.wAttributes,
            self.srWindow.Top, self.srWindow.Left,
            self.srWindow.Bottom, self.srWindow.Right,
            self.dwMaximumWindowSize.Y, self.dwMaximumWindowSize.X,
        )


INVALID_HANDLE_VALUE = HANDLE(-1)


class Win32APIError(Exception):
    pass


def _check_handle(result, func, _) -> int:

    if result == INVALID_HANDLE_VALUE.value:
        raise Win32APIError(f"{func.__name__}() failed")

    return result


def _check_success(result, func, _) -> None:

    if not result:
        raise Win32APIError(f"{func.__name__}() failed")


_windll = _LibraryLoader(_WinDLL)


GetStdHandle = _windll.kernel32.GetStdHandle
GetStdHandle.argtypes = [
    DWORD,
]
GetStdHandle.restype = HANDLE
GetStdHandle.errcheck = _check_handle

FillConsoleOutputCharacterW = _windll.kernel32.FillConsoleOutputCharacterW
FillConsoleOutputCharacterW.argtypes = [HANDLE, WCHAR, DWORD, COORD, LPDWORD]
FillConsoleOutputCharacterW.restype = BOOL
FillConsoleOutputCharacterW.errcheck = _check_success

GetConsoleMode = _windll.kernel32.GetConsoleMode
GetConsoleMode.argtypes = [HANDLE, LPDWORD]
GetConsoleMode.restype = BOOL
GetConsoleMode.errcheck = _check_success

GetConsoleScreenBufferInfo = _windll.kernel32.GetConsoleScreenBufferInfo
GetConsoleScreenBufferInfo.argtypes = [HANDLE, _POINTER(ConsoleScreenBufferInfo)]
GetConsoleScreenBufferInfo.restype = BOOL
GetConsoleScreenBufferInfo.errcheck = _check_success

ScrollConsoleScreenBufferW = _windll.kernel32.ScrollConsoleScreenBufferW
ScrollConsoleScreenBufferW.argtypes = [HANDLE, PSMALL_RECT, PSMALL_RECT, COORD,
                                       _POINTER(CharInfo)]
ScrollConsoleScreenBufferW.restype = BOOL
ScrollConsoleScreenBufferW.errcheck = _check_success

SetConsoleCursorPosition = _windll.kernel32.SetConsoleCursorPosition
SetConsoleCursorPosition.argtypes = [HANDLE, COORD]
SetConsoleCursorPosition.restype = BOOL
SetConsoleCursorPosition.errcheck = _check_success

SetConsoleMode = _windll.kernel32.SetConsoleMode
SetConsoleMode.argtypes = [HANDLE, DWORD]
SetConsoleMode.restype = BOOL
SetConsoleMode.errcheck = _check_success

WriteConsoleW = _windll.kernel32.WriteConsoleW
WriteConsoleW.argtypes = [HANDLE, LPWSTR, DWORD, LPDWORD, LPVOID]
WriteConsoleW.restype = BOOL
WriteConsoleW.errcheck = _check_success

WriteConsoleOutputCharacterW = _windll.kernel32.WriteConsoleOutputCharacterW
WriteConsoleOutputCharacterW.argtypes = [HANDLE, LPCWSTR, DWORD, COORD, LPDWORD]
WriteConsoleOutputCharacterW.restype = BOOL
WriteConsoleOutputCharacterW.errcheck = _check_success
