#!/usr/bin/env python3

import asyncio as _asyncio

from asyncio import Event as _Signal
from functools import partial as _partial

from . import events as _events

from .elements import (
    _Container,
    _Element,
)

from .console import Console as _Console


class GUI(_Container):

    def __init__(self, element: _Element, *, console: _Console = None,
                 **kwargs) -> None:

        super().__init__(**kwargs)

        self.element = element
        self.console = console if console is not None else _Console()

        def_rows, def_cols = element.get_def()
        tty_rows, tty_cols = console.visible_dims()

        self.console.resize_buffer(min(def_rows, tty_rows), tty_cols)

        self.element.parent = self
        self.invalidate_child(self.element)
        # self._refresh()

    def _refresh(self) -> None:

        if not self._refresh_children:
            return

        buffer = self.console.get_buffer()

        if self.element in self._refresh_children:
            self.element.render(buffer)

        self._refresh_children.clear()

        _asyncio.get_running_loop().call_soon(self.console.flush)

    def invalidate_child(self, child: _Element) -> bool:

        if not super().invalidate_child(child):
            return False

        _asyncio.get_running_loop().call_soon(self._refresh)
        return True

    def _event_callback(self, event: _events.Event,
                        *, quit_signal: _Signal) -> None:

        if isinstance(event, _events.QuitEvent):
            quit_signal.set()
            return

        self.element.handle_event(event)

    async def handle(self) -> None:

        quit_signal = _Signal()
        token = self.console.register_event_handler(
            _partial(self._event_callback, quit_signal=quit_signal)
        )

        await quit_signal.wait()

        self.console.unregister_event_handler(token)
