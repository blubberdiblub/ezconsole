#!/usr/bin/env python3

from typing import (
    Any as _Any,
    Callable as _Callable,
)

import asyncio as _asyncio
import logging as _logging
import threading as _threading

from asyncio.windows_events import (
    WindowsProactorEventLoopPolicy as _EventLoopPolicy,
)

from concurrent.futures import ThreadPoolExecutor as _Executor

from ctypes import byref as _byref

from ._console import _Console

from ._win32api import (
    DWORD as _DWORD,

    Coord as _Coord,
    SMALL_RECT as _SMALL_RECT,

    CharInfo as _CharInfo,
    ConsoleScreenBufferInfo as _ConsoleScreenBufferInfo,
    SecurityAttributes as _SecurityAttributes,
    KeyEventRecord as _KeyEventRecord,
    InputRecord as _InputRecord,

    INVALID_HANDLE_VALUE as _INVALID_HANDLE_VALUE,

    CloseHandle as _CloseHandle,
    CreateFileW as _CreateFileW,

    FillConsoleOutputCharacterW as _FillConsoleOutputCharacterW,
    FlushConsoleInputBuffer as _FlushConsoleInputBuffer,
    GetConsoleMode as _GetConsoleMode,
    GetConsoleScreenBufferInfo as _GetConsoleScreenBufferInfo,
    ReadConsoleInputW as _ReadConsoleInputW,
    ScrollConsoleScreenBufferW as _ScrollConsoleScreenBufferW,
    SetConsoleCursorPosition as _SetConsoleCursorPosition,
    SetConsoleMode as _SetConsoleMode,
    WriteConsoleInputW as _WriteConsoleInputW,
    WriteConsoleOutputCharacterW as _WriteConsoleOutputCharacterW,
)

from .. import events as _events


_log = _logging.getLogger(__name__)

# noinspection PyTypeChecker
_asyncio.set_event_loop_policy(_EventLoopPolicy())


class Win32Console(_Console):

    def __init__(self) -> None:

        self._range_height = 0
        self._fill_char = ' '

        self._executor = None

        self._output = None
        self._saved_output_mode = None
        self._buffer_info = _ConsoleScreenBufferInfo()

        self._input_handler = None
        self._input_future = None

        self._executor = _Executor(max_workers=1)

        input_ = _CreateFileW('CONIN$', 0xc0000000, 0x3,
                              _byref(_SecurityAttributes(None, True)),
                              3, 0x80, None)

        self._output = _CreateFileW('CONOUT$', 0xc0000000, 0x3,
                                    _byref(_SecurityAttributes(None, True)),
                                    3, 0x80, None)

        mode = _DWORD()
        _GetConsoleMode(self._output, _byref(mode))
        self._saved_output_mode = mode.value

        _SetConsoleMode(self._output, self._saved_output_mode | 0x0018)

        self._update_buffer_info()

        self._input_handler = _ConsoleInputHandler(input_, close=True)

        loop = _asyncio.get_event_loop()
        self._input_future = loop.run_in_executor(self._executor,
                                                  self._input_handler.handle)

    def __del__(self) -> None:

        self.close(timeout=0)

    # noinspection PyBroadException
    def close(self, timeout: float = 0.1) -> None:

        input_future, self._input_future = self._input_future, None
        input_handler, self._input_handler = self._input_handler, None
        output, self._output = self._output, None
        executor, self._executor = self._executor, None
        self._buffer_info = None

        if input_future is not None:

            try:
                input_future.cancel()

            except Exception:
                _log.exception("unable to cancel input handler during cleanup")

        if input_handler is not None:

            try:
                input_handler.shutdown()

            except Exception:
                _log.exception(
                    "unable to shutdown input handler during cleanup"
                )

        if (self._saved_output_mode is not None and
                output is not None and output != _INVALID_HANDLE_VALUE.value):

            try:
                _SetConsoleMode(output, self._saved_output_mode)

            except Exception:
                _log.exception(
                    "unable to reset console output mode during cleanup"
                )

        if executor is not None:

            try:
                executor.shutdown(wait=False)

            except Exception:
                _log.exception("unable to shutdown executor during cleanup")

    def _update_buffer_info(self) -> None:

        _GetConsoleScreenBufferInfo(self._output, _byref(self._buffer_info))

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
            _ScrollConsoleScreenBufferW(
                    self._output, _SMALL_RECT(0, 0, max_x, y - 1), None,
                    _Coord(0, -missing_lines),
                    _CharInfo(self._fill_char, self._buffer_info.wAttributes)
            )

            self._range_height += missing_lines
            if self._range_height == height:
                return height

        delta = height - self._range_height
        if delta < 0:
            y += delta

        scroll_region = _SMALL_RECT(0, y, max_x, max_y)
        _ScrollConsoleScreenBufferW(
                self._output, scroll_region, scroll_region,
                _Coord(0, y + delta),
                _CharInfo(self._fill_char, self._buffer_info.wAttributes)
        )

        self._range_height += delta
        self._buffer_info.dwCursorPosition.Y += delta

        _SetConsoleCursorPosition(self._output,
                                  self._buffer_info.dwCursorPosition)

        assert self._range_height == height
        return height

    def line_at(self, y: int, text: str, tail: int = 0) -> None:

        y += self._buffer_info.dwCursorPosition.Y - self._range_height
        n = len(text)

        written = _DWORD()
        _WriteConsoleOutputCharacterW(self._output, text, n, _Coord(0, y),
                                      _byref(written))

        if tail <= 0:
            return

        _FillConsoleOutputCharacterW(self._output, self._fill_char, tail,
                                     _Coord(n, y), _byref(written))

    def register_input_callback(self, callback: _Callable) -> _Any:

        return self._input_handler.register_callback(callback)

    def unregister_input_callback(self, token: _Any) -> None:

        self._input_handler.unregister_callback(token)


class _ConsoleInputHandler:

    def __init__(self, handle, close=False) -> None:

        self._handle = handle
        self._close = close
        self._saved_mode = None
        self._callback = None
        self._callback_lock = None
        self._shutdown_signal = None

        mode = _DWORD()
        _GetConsoleMode(self._handle, _byref(mode))
        self._saved_mode = mode.value

        _SetConsoleMode(self._handle, self._saved_mode & ~0x0007 | 0x0018)

        self._callback_lock = _threading.Lock()
        self._shutdown_signal = _threading.Event()

    # noinspection PyBroadException
    def __del__(self) -> None:

        handle, self._handle = self._handle, None
        saved_mode, self._saved_mode = self._saved_mode, None

        if handle is not None and handle != _INVALID_HANDLE_VALUE.value:

            try:
                _FlushConsoleInputBuffer(handle)

            except Exception:
                _log.exception(
                    "unable to flush console input buffer during cleanup"
                )

            if saved_mode is not None:

                try:
                    _SetConsoleMode(handle, saved_mode)

                except Exception:
                    _log.exception(
                        "unable to reset console input mode during cleanup"
                    )

            if self._close:

                try:
                    _CloseHandle(handle)

                except Exception:
                    _log.exception(
                        "unable to close console input handle during cleanup"
                    )

    def shutdown(self) -> None:

        self._shutdown_signal.set()

        input_record = _InputRecord(EventType=0x1, KeyEvent=_KeyEventRecord(
            wVirtualKeyCode=0xff,
            wVirtualScanCode=0xffff,
        ))
        written = _DWORD()
        _WriteConsoleInputW(self._handle, input_record, 1, _byref(written))

    def handle(self) -> None:

        # noinspection PyTypeChecker,PyCallingNonCallable
        buffer = (_InputRecord * 100)()
        read = _DWORD()

        while not self._shutdown_signal.is_set():

            _ReadConsoleInputW(self._handle, buffer, len(buffer), _byref(read))

            if self._shutdown_signal.is_set():
                break

            for input_record in buffer[:read.value]:

                if input_record.EventType != 0x0001:
                    continue

                key_event = input_record.KeyEvent
                if not key_event.bKeyDown:
                    continue

                vk = key_event.wVirtualKeyCode
                if vk == 0x1b:
                    event = _events.QuitEvent()

                elif vk == 0x26:
                    event = _events.UpNavEvent()

                elif vk == 0x28:
                    event = _events.DownNavEvent()

                else:
                    continue

                with self._callback_lock:
                    if self._callback is None:
                        continue

                    loop, callback = self._callback

                loop.call_soon_threadsafe(callback, event)

    def register_callback(self, callback: _Callable) -> _Any:

        pair = _asyncio.get_running_loop(), callback

        with self._callback_lock:

            if self._callback is not None:
                raise NotImplementedError("cannot register multiple callbacks")

            self._callback = pair

        return hash(pair)

    def unregister_callback(self, token: _Any) -> None:

        with self._callback_lock:

            if self._callback is None:
                raise ValueError("no callback has been registered")

            if hash(self._callback) != token:
                raise ValueError("token mismatch")

            self._callback = None
