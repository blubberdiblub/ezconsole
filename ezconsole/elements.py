#!/usr/bin/env python3

from typing import (
    Optional as _Optional,
    Sequence as _Sequence,
    Tuple as _Tuple,
)

from abc import (
    ABCMeta as _ABCMeta,
    abstractmethod as _abstractmethod,
)

import numpy as _np

from . import events as _events


class _Element(metaclass=_ABCMeta):

    def __init__(self, **kwargs) -> None:

        self._min = 0, 0
        self._def = 0, 0
        self._max = float('inf'), float('inf')

        super().__init__(**kwargs)

    def get_min(self) -> _Tuple[int, int]:

        return self._min

    def get_def(self) -> _Tuple[int, int]:

        return self._def

    @_abstractmethod
    def render(self, cells: _np.ndarray) -> None:

        raise NotImplementedError

    def handle_event(self, event: _events.Event) -> bool:

        return False


class Choice(_Element):

    def __init__(self, items: _Sequence[str], **kwargs) -> None:

        super().__init__(**kwargs)

        self._items = list(items)
        self._choice = 0

        width = max(len(item) for item in self._items)
        height = len(self._items)

        self._min = min(3, height), min(3, width) + 2
        self._def = height, width + 2

    def render(self, cells: _np.ndarray) -> None:

        rows, cols = cells.shape
        lines = _np.ndarray((rows,), dtype=f'=U{cols}', buffer=cells)

        count = min(len(self._items), rows)

        lines[:count] = self._items[:count]
        lines[count:] = ''

    def handle_event(self, event: _events.Event) -> bool:

        if not isinstance(event, _events.VerticalNavEvent):

            return False

        if not 0 <= self._choice <= len(self._items):

            self._choice = 0

        self._choice += event.y
        self._choice %= len(self._items) + 1

        return True

    def get_choice(self) -> _Optional[int]:

        if not 0 < self._choice <= len(self._items):

            return None

        return self._choice - 1
