#!/usr/bin/env python3

from ctypes import (
    sizeof as _sizeof,
    POINTER as _POINTER,
    Structure as _Structure,
    Union as _Union,
    LibraryLoader as _LibraryLoader,
    WinDLL as _WinDLL,
)

# noinspection PyProtectedMember
from ctypes.wintypes import (
    BOOL,
    DWORD,
    HANDLE,
    LPCWSTR,
    LPDWORD,
    LPVOID,
    LPWSTR,
    WCHAR,
    WORD,

    _COORD,
    SMALL_RECT,
    PSMALL_RECT,
)


class Coord(_COORD):

    def __repr__(self):

        return f"{type(self).__name__}(X={self.X}, Y={self.Y})"


class CharInfo(_Structure):

    _fields_ = [
        ('Char', WCHAR),
        ('Attributes', WORD),
    ]


class ConsoleScreenBufferInfo(_Structure):

    _fields_ = [
        ('dwSize', Coord),
        ('dwCursorPosition', Coord),
        ('wAttributes', WORD),
        ('srWindow', SMALL_RECT),
        ('dwMaximumWindowSize', Coord),
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


class SecurityAttributes(_Structure):

    _fields_ = [
        ('nLength', DWORD),
        ('lpSecurityDescriptor', LPVOID),
        ('bInheritHandle', BOOL),
    ]

    def __init__(self, security_descriptor: LPVOID = None,
                 inherit_handle: bool = False) -> None:

        super().__init__(
            nLength=_sizeof(self),
            lpSecurityDescriptor=security_descriptor,
            bInheritHandle=inherit_handle,
        )

    def __repr__(self) -> str:

        return (f"{type(self).__name__}("
                f"security_descriptor={self.lpSecurityDescriptor}, "
                f"inherit_handle={bool(self.bInheritHandle)})")


class KeyEventRecord(_Structure):

    _fields_ = [
        ('bKeyDown', BOOL),
        ('wRepeatCount', WORD),
        ('wVirtualKeyCode', WORD),
        ('wVirtualScanCode', WORD),
        ('UnicodeChar', WCHAR),
        ('dwControlKeyState', DWORD),
    ]

    def __repr__(self) -> str:

        return (f"{type(self).__name__}("
                f"{bool(self.bKeyDown)}, "
                f"{self.wRepeatCount}, "
                f"{self.wVirtualKeyCode:#x}, "
                f"{self.wVirtualScanCode:#x}, "
                f"{self.UnicodeChar!r}, "
                f"{self.dwControlKeyState:#x})")


class MouseEventRecord(_Structure):

    _fields_ = [
        ('dwMousePosition', Coord),
        ('dwButtonState', DWORD),
        ('dwControlKeyState', DWORD),
        ('dwEventFlags', DWORD),
    ]

    def __repr__(self) -> str:

        return (f"{type(self).__name__}("
                f"dwMousePosition={self.dwMousePosition}, "
                f"dwButtonState={self.dwButtonState}, "
                f"dwControlKeyState={self.dwControlKeyState}, "
                f"dwEventFlags={self.dwEventFlags})")


class WindowBufferSizeRecord(_Structure):

    _fields_ = [
        ('dwSize', Coord),
    ]

    def __repr__(self) -> str:

        return (f"{type(self).__name__}("
                f"dwSize={self.dwSize})")


class _Event(_Union):

    _fields_ = [
        ('KeyEvent', KeyEventRecord),
        ('MouseEvent', MouseEventRecord),
        ('WindowBufferSizeEvent', WindowBufferSizeRecord),
    ]


class InputRecord(_Structure):

    _anonymous_ = ['Event']
    _fields_ = [
        ('EventType', WORD),
        ('Event', _Event),
    ]

    def __repr__(self) -> str:

        if self.EventType == 0x0001:
            event_repr = f"KeyEvent={self.KeyEvent!r}"

        elif self.EventType == 0x0002:
            event_repr = f"MouseEvent={self.MouseEvent!r}"

        elif self.EventType == 0x0004:
            event_repr = f"WindowBufferSizeEvent={self.WindowBufferSizeEvent!r}"

        else:
            event_repr = f"Event={self.Event}"

        return (f"{type(self).__name__}("
                f"EventType={self.EventType:#x}, {event_repr})")


INVALID_HANDLE_VALUE = HANDLE(-1)


class Win32APIError(Exception):
    pass


def _errcheck_return_handle(result, func, _) -> int:

    if result == INVALID_HANDLE_VALUE.value:
        raise Win32APIError(f"{func.__name__}() failed")

    return result


def _errcheck_return_success(result, func, _) -> None:

    if not result:
        raise Win32APIError(f"{func.__name__}() failed")


_windll = _LibraryLoader(_WinDLL)


CloseHandle = _windll.kernel32.CloseHandle
CloseHandle.argtypes = [HANDLE]
CloseHandle.restype = BOOL
CloseHandle.errcheck = _errcheck_return_success

CreateFileW = _windll.kernel32.CreateFileW
CreateFileW.argtypes = [LPCWSTR, DWORD, DWORD, _POINTER(SecurityAttributes),
                        DWORD, DWORD, HANDLE]
CreateFileW.restype = HANDLE
CreateFileW.errcheck = _errcheck_return_handle

GetStdHandle = _windll.kernel32.GetStdHandle
GetStdHandle.argtypes = [DWORD]
GetStdHandle.restype = HANDLE
GetStdHandle.errcheck = _errcheck_return_handle

CompareObjectHandles = _windll.kernelbase.CompareObjectHandles
CompareObjectHandles.argtypes = [HANDLE, HANDLE]
CompareObjectHandles.restype = BOOL

FillConsoleOutputCharacterW = _windll.kernel32.FillConsoleOutputCharacterW
FillConsoleOutputCharacterW.argtypes = [HANDLE, WCHAR, DWORD, Coord, LPDWORD]
FillConsoleOutputCharacterW.restype = BOOL
FillConsoleOutputCharacterW.errcheck = _errcheck_return_success

FlushConsoleInputBuffer = _windll.kernel32.FlushConsoleInputBuffer
FlushConsoleInputBuffer.argtypes = [HANDLE]
FlushConsoleInputBuffer.restype = BOOL
FlushConsoleInputBuffer.errcheck = _errcheck_return_success

GetConsoleMode = _windll.kernel32.GetConsoleMode
GetConsoleMode.argtypes = [HANDLE, LPDWORD]
GetConsoleMode.restype = BOOL
GetConsoleMode.errcheck = _errcheck_return_success

GetConsoleScreenBufferInfo = _windll.kernel32.GetConsoleScreenBufferInfo
GetConsoleScreenBufferInfo.argtypes = [HANDLE,
                                       _POINTER(ConsoleScreenBufferInfo)]
GetConsoleScreenBufferInfo.restype = BOOL
GetConsoleScreenBufferInfo.errcheck = _errcheck_return_success

ReadConsoleInputW = _windll.kernel32.ReadConsoleInputW
ReadConsoleInputW.argtypes = [HANDLE, _POINTER(InputRecord), DWORD, LPDWORD]
ReadConsoleInputW.restype = BOOL
ReadConsoleInputW.errcheck = _errcheck_return_success

ScrollConsoleScreenBufferW = _windll.kernel32.ScrollConsoleScreenBufferW
ScrollConsoleScreenBufferW.argtypes = [HANDLE, PSMALL_RECT, PSMALL_RECT, Coord,
                                       _POINTER(CharInfo)]
ScrollConsoleScreenBufferW.restype = BOOL
ScrollConsoleScreenBufferW.errcheck = _errcheck_return_success

SetConsoleCursorPosition = _windll.kernel32.SetConsoleCursorPosition
SetConsoleCursorPosition.argtypes = [HANDLE, Coord]
SetConsoleCursorPosition.restype = BOOL
SetConsoleCursorPosition.errcheck = _errcheck_return_success

SetConsoleMode = _windll.kernel32.SetConsoleMode
SetConsoleMode.argtypes = [HANDLE, DWORD]
SetConsoleMode.restype = BOOL
SetConsoleMode.errcheck = _errcheck_return_success

WriteConsoleW = _windll.kernel32.WriteConsoleW
WriteConsoleW.argtypes = [HANDLE, LPWSTR, DWORD, LPDWORD, LPVOID]
WriteConsoleW.restype = BOOL
WriteConsoleW.errcheck = _errcheck_return_success

WriteConsoleInputW = _windll.kernel32.WriteConsoleInputW
WriteConsoleInputW.argtypes = [HANDLE, _POINTER(InputRecord), DWORD, LPDWORD]
WriteConsoleInputW.restype = BOOL
WriteConsoleInputW.errcheck = _errcheck_return_success

WriteConsoleOutputCharacterW = _windll.kernel32.WriteConsoleOutputCharacterW
WriteConsoleOutputCharacterW.argtypes = [HANDLE, LPCWSTR, DWORD, Coord, LPDWORD]
WriteConsoleOutputCharacterW.restype = BOOL
WriteConsoleOutputCharacterW.errcheck = _errcheck_return_success
