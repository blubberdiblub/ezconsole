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
        return '<(%d,%d),(%d,%d),%04x,((%d,%d),(%d,%d)),(%d,%d)>' % (
            self.dwSize.Y, self.dwSize.X,
            self.dwCursorPosition.Y, self.dwCursorPosition.X,
            self.wAttributes,
            self.srWindow.Top, self.srWindow.Left,
            self.srWindow.Bottom, self.srWindow.Right,
            self.dwMaximumWindowSize.Y, self.dwMaximumWindowSize.X,
        )


class _CharInfo(_Structure):

    _fields_ = [
        ('Char', _wintypes.WCHAR),
        ('Attributes', _wintypes.WORD),
    ]


_INVALID_HANDLE_VALUE = _wintypes.HANDLE(-1)


_windll = _LibraryLoader(_WinDLL)

_GetStdHandle = _windll.kernel32.GetStdHandle
_GetStdHandle.argtypes = [
    _wintypes.DWORD,
]
_GetStdHandle.restype = _wintypes.HANDLE

_FillConsoleOutputCharacterW = _windll.kernel32.FillConsoleOutputCharacterW
_FillConsoleOutputCharacterW.argtypes = [
    _wintypes.HANDLE,
    _wintypes.WCHAR,
    _wintypes.DWORD,
    _wintypes._COORD,
    _wintypes.LPDWORD,
]
_FillConsoleOutputCharacterW.restype = _wintypes.BOOL

_GetConsoleMode = _windll.kernel32.GetConsoleMode
_GetConsoleMode.argtypes = [
    _wintypes.HANDLE,
    _wintypes.LPDWORD,
]
_GetConsoleMode.restype = _wintypes.BOOL

_GetConsoleScreenBufferInfo = _windll.kernel32.GetConsoleScreenBufferInfo
_GetConsoleScreenBufferInfo.argtypes = [
    _wintypes.HANDLE,
    _POINTER(_ConsoleScreenBufferInfo),
]
_GetConsoleScreenBufferInfo.restype = _wintypes.BOOL

_ScrollConsoleScreenBufferW = _windll.kernel32.ScrollConsoleScreenBufferW
_ScrollConsoleScreenBufferW.argtypes = [
    _wintypes.HANDLE,
    _wintypes.PSMALL_RECT,
    _wintypes.PSMALL_RECT,
    _wintypes._COORD,
    _POINTER(_CharInfo),
]
_ScrollConsoleScreenBufferW.restype = _wintypes.BOOL

_SetConsoleCursorPosition = _windll.kernel32.SetConsoleCursorPosition
_SetConsoleCursorPosition.argtypes = [
    _wintypes.HANDLE,
    _wintypes._COORD,
]
_SetConsoleCursorPosition.restype = _wintypes.BOOL

_SetConsoleMode = _windll.kernel32.SetConsoleMode
_SetConsoleMode.argtypes = [
    _wintypes.HANDLE,
    _wintypes.DWORD,
]
_SetConsoleMode.restype = _wintypes.BOOL

_WriteConsoleW = _windll.kernel32.WriteConsoleW
_WriteConsoleW.argtypes = [
    _wintypes.HANDLE,
    _wintypes.LPWSTR,
    _wintypes.DWORD,
    _wintypes.LPDWORD,
    _wintypes.LPVOID,
]
_WriteConsoleW.restype = _wintypes.BOOL

_WriteConsoleOutputCharacterW = _windll.kernel32.WriteConsoleOutputCharacterW
_WriteConsoleOutputCharacterW.argtypes = [
    _wintypes.HANDLE,
    _wintypes.LPCWSTR,
    _wintypes.DWORD,
    _wintypes._COORD,
    _wintypes.LPDWORD,
]
_WriteConsoleOutputCharacterW.restype = _wintypes.BOOL


class Win32Console(_Console):

    def __init__(self) -> None:

        self._range_height = 0
        self._fill_char = ' '

        self._handle = None
        self._saved_mode = 0x0003
        self._buffer_info = _ConsoleScreenBufferInfo()

        self._handle = _GetStdHandle(-11)
        if self._handle == _INVALID_HANDLE_VALUE.value:
            raise SystemError("GetStdHandle() failed")

        mode = _wintypes.DWORD()
        if not _GetConsoleMode(self._handle, _byref(mode)):
            raise SystemError("GetConsoleMode() failed")
        self._saved_mode = mode.value

        if not _SetConsoleMode(self._handle, self._saved_mode | 0x001f):
            raise SystemError("SetConsoleMode() failed")

        self._update_buffer_info()

    def __del__(self) -> None:

        handle, self._handle = self._handle, None
        buffer_info, self._buffer_info = self._buffer_info, None

        if handle is None or handle == _INVALID_HANDLE_VALUE.value:
            return

        _SetConsoleMode(handle, self._saved_mode)

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

    def request_size(self, height: int) -> int:

        if height < 0:
            raise ValueError("n cannot be negative")

        max_y = self._buffer_info.dwSize.Y - 1
        max_height = min(max_y, max(self._buffer_info.srWindow.Bottom -
                                    self._buffer_info.srWindow.Top, 3))

        if height > max_height:
            height = max_height

        if height == self._range_height:
            return height

        max_x = self._buffer_info.dwSize.X - 1
        y = self._buffer_info.dwCursorPosition.Y

        missing_lines = (height - self._range_height) - (max_y - y)
        if missing_lines > 0:
            if not _ScrollConsoleScreenBufferW(self._handle,
                                               _wintypes.SMALL_RECT(0, 0, max_x,
                                                                    y - 1),
                                               None,
                                               _wintypes._COORD(0,
                                                                -missing_lines),
                                               _CharInfo(self._fill_char,
                                                         self._buffer_info.wAttributes)):
                raise SystemError("ScrollConsoleScreenBufferW() failed")

            self._range_height += missing_lines
            if self._range_height == height:
                return height

        delta = height - self._range_height
        if delta < 0:
            y += delta

        scroll_region = _wintypes.SMALL_RECT(0, y, max_x, max_y)
        if not _ScrollConsoleScreenBufferW(self._handle,
                                           scroll_region, scroll_region,
                                           _wintypes._COORD(0, y + delta),
                                           _CharInfo(self._fill_char,
                                                     self._buffer_info.wAttributes)):
            raise SystemError("ScrollConsoleScreenBufferW() failed")

        self._range_height += delta
        self._buffer_info.dwCursorPosition.Y += delta

        if not _SetConsoleCursorPosition(self._handle,
                                         self._buffer_info.dwCursorPosition):
            raise SystemError("SetConsoleCursorPosition() failed")

        assert self._range_height == height
        return height

    def line_at(self, y: int, text: str, tail: int = 0) -> None:

        y += self._buffer_info.dwCursorPosition.Y - self._range_height
        n = len(text)

        written = _wintypes.DWORD()
        if not _WriteConsoleOutputCharacterW(self._handle, text, n,
                                             _wintypes._COORD(0, y),
                                             _byref(written)):
            raise SystemError("WriteConsoleOutputCharacterW() failed")

        if tail <= 0:
            return

        if not _FillConsoleOutputCharacterW(self._handle, self._fill_char, tail,
                                            _wintypes._COORD(n, y),
                                            _byref(written)):
            raise SystemError("FillConsoleOutputCharacterW() failed")
