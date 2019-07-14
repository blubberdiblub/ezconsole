#!/usr/bin/env python3

from typing import Sequence as _Sequence, Tuple as _Tuple

import numpy as _np


class _Element:

    def __init__(self, **kwargs) -> None:

        self._min = 0, 0
        self._def = 0, 0
        self._max = float("inf"), float("inf")

        super().__init__(**kwargs)

    def get_min(self) -> _Tuple[int, int]:

        return self._min

    def render(self, cells: _np.ndarray) -> None:

        raise NotImplementedError


class Choice(_Element):

    def __init__(self, items: _Sequence[str], **kwargs) -> None:

        super().__init__(**kwargs)

        self._items = list(items)

        self._def = len(self._items), max(len(item) for item in self._items)
        self._min = self._def

    def render(self, cells: _np.ndarray) -> None:

        rows, cols = cells.shape
        lines = _np.ndarray((rows,), dtype=f'=U{cols}', buffer=cells)

        count = min(len(self._items), rows)

        lines[:count] = self._items[:count]
        lines[count:] = ''
