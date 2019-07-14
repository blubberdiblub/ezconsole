#!/usr/bin/env python3

from .elements import _Element
from .console import Console as _Console


def ez_dialog(element: _Element, console: _Console = None):

    if console is None:
        console = _Console()

    min_rows, min_cols = element.get_min()
    tty_rows, tty_cols = console.visible_dims()

    console.resize_buffer(min(min_rows, tty_rows), tty_cols)
    element.render(console.get_buffer())
    console.flush()
