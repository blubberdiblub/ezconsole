#!/usr/bin/env python3

__all__ = ['Console']


import sys as _sys


if _sys.platform == 'win32':
    from .win32 import Win32Console as Console

else:
    from .posix import POSIXConsole as Console
