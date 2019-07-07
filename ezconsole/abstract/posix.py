#!/usr/bin/env python3

import curses as _curses

from ._console import _Console


class POSIXConsole(_Console):

    def __init__(self) -> None:

        import os
        import sys

        self._stdout = sys.__stdout__

        self._term = _curses.setupterm(term=os.environ.get("TERM", "unknown"),
                                       fd=self._stdout.fileno())

    def print(self, s: str, flush: bool = False) -> None:
        print(s, end='\r\n', flush=flush, file=self._stdout)

    def get_width(self) -> int:
        return _curses.tigetnum('cols')

    def get_height(self) -> int:
        return _curses.tigetnum('lines')

    def get_colors(self) -> int:
        return _curses.tigetnum('colors')
