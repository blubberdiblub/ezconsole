#!/usr/bin/env python3

from ctypes import byref as _byref

from ._console import _Console

from ._win32api import (
    DWORD as _DWORD,

    COORD as _COORD,
    SMALL_RECT as _SMALL_RECT,

    CharInfo as _CharInfo,
    ConsoleScreenBufferInfo as _ConsoleScreenBufferInfo,

    INVALID_HANDLE_VALUE as _INVALID_HANDLE_VALUE,

    GetStdHandle as _GetStdHandle,

    FillConsoleOutputCharacterW as _FillConsoleOutputCharacterW,
    GetConsoleMode as _GetConsoleMode,
    GetConsoleScreenBufferInfo as _GetConsoleScreenBufferInfo,
    ScrollConsoleScreenBufferW as _ScrollConsoleScreenBufferW,
    SetConsoleCursorPosition as _SetConsoleCursorPosition,
    SetConsoleMode as _SetConsoleMode,
    WriteConsoleOutputCharacterW as _WriteConsoleOutputCharacterW,
)


class Win32Console(_Console):

    def __init__(self) -> None:

        self._range_height = 0
        self._fill_char = ' '

        self._handle = None
        self._saved_mode = 0x0003
        self._buffer_info = _ConsoleScreenBufferInfo()

        self._handle = _GetStdHandle(-11)
        if self._handle == _INVALID_HANDLE_VALUE.value:
            raise RuntimeError("GetStdHandle() failed")

        mode = _DWORD()
        if not _GetConsoleMode(self._handle, _byref(mode)):
            raise RuntimeError("GetConsoleMode() failed")
        self._saved_mode = mode.value

        if not _SetConsoleMode(self._handle, self._saved_mode | 0x001f):
            raise RuntimeError("SetConsoleMode() failed")

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
            raise RuntimeError("GetConsoleScreenBufferInfo() failed")

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
            if not _ScrollConsoleScreenBufferW(
                    self._handle, _SMALL_RECT(0, 0, max_x, y - 1), None,
                    _COORD(0, -missing_lines),
                    _CharInfo(self._fill_char, self._buffer_info.wAttributes)
            ):
                raise RuntimeError("ScrollConsoleScreenBufferW() failed")

            self._range_height += missing_lines
            if self._range_height == height:
                return height

        delta = height - self._range_height
        if delta < 0:
            y += delta

        scroll_region = _SMALL_RECT(0, y, max_x, max_y)
        if not _ScrollConsoleScreenBufferW(
                self._handle, scroll_region, scroll_region,
                _COORD(0, y + delta),
                _CharInfo(self._fill_char, self._buffer_info.wAttributes)
        ):
            raise RuntimeError("ScrollConsoleScreenBufferW() failed")

        self._range_height += delta
        self._buffer_info.dwCursorPosition.Y += delta

        if not _SetConsoleCursorPosition(self._handle,
                                         self._buffer_info.dwCursorPosition):
            raise RuntimeError("SetConsoleCursorPosition() failed")

        assert self._range_height == height
        return height

    def line_at(self, y: int, text: str, tail: int = 0) -> None:

        y += self._buffer_info.dwCursorPosition.Y - self._range_height
        n = len(text)

        written = _DWORD()
        if not _WriteConsoleOutputCharacterW(self._handle, text, n,
                                             _COORD(0, y), _byref(written)):
            raise RuntimeError("WriteConsoleOutputCharacterW() failed")

        if tail <= 0:
            return

        if not _FillConsoleOutputCharacterW(self._handle, self._fill_char, tail,
                                            _COORD(n, y), _byref(written)):
            raise RuntimeError("FillConsoleOutputCharacterW() failed")
