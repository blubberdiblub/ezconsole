#!/usr/bin/env python3

from asyncio import Event as _Signal
from functools import partial as _partial

from . import events as _events

from .elements import _Element
from .console import Console as _Console


class GUI:

    def __init__(self, element: _Element, console: _Console = None) -> None:

        self.element = element
        self.console = console if console is not None else _Console()

        def_rows, def_cols = element.get_def()
        tty_rows, tty_cols = console.visible_dims()

        self.console.resize_buffer(min(def_rows, tty_rows), tty_cols)
        self.element.render(self.console.get_buffer())
        self.console.flush()

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
