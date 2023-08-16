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

import weakref as _weakref

import numpy as _np

from . import events as _events


class _Container(metaclass=_ABCMeta):

    def __init__(self, **kwargs) -> None:

        super().__init__(**kwargs)

        self._refresh_children = _weakref.WeakSet()

    def invalidate_child(self, child: '_Element') -> bool:

        if child in self._refresh_children:
            return False

        self._refresh_children.add(child)
        return True


class _Element(metaclass=_ABCMeta):

    def __init__(self, *, parent: _Container = None, **kwargs) -> None:

        super().__init__(**kwargs)

        self._parent = None
        self._needs_refresh = True
        self._refresh_children = None

        self._min = 0, 0
        self._def = 0, 0
        self._max = float('inf'), float('inf')

        self.parent = parent

    @property
    def parent(self) -> _Optional[_Container]:

        return self._parent()

    @parent.setter
    def parent(self, parent: _Optional[_Container]) -> None:

        if parent is None:
            self._parent = type(None)
            return

        self._parent = _weakref.ref(parent)

        if self._needs_refresh:
            parent.invalidate_child(self)

    def get_min(self) -> _Tuple[int, int]:

        return self._min

    def get_def(self) -> _Tuple[int, int]:

        return self._def

    @_abstractmethod
    def render(self, cells: _np.ndarray) -> None:

        raise NotImplementedError

    def invalidate(self) -> bool:

        if self._needs_refresh:
            return False

        self._needs_refresh = True

        parent = self._parent()
        if parent is not None:
            parent.invalidate_child(self)

        return True

    def handle_event(self, event: _events.Event) -> bool:

        return False


# noinspection PyAbstractClass
class _ContainerElement(_Element, _Container):

    def invalidate_child(self, child: _Element) -> bool:

        if not super().invalidate_child(child):
            return False

        parent = self._parent()
        if parent is not None:
            parent.invalidate_child(self)

        return True


class Choice(_Element):

    def __init__(self, items: _Sequence[str], **kwargs) -> None:

        super().__init__(**kwargs)

        self._items = list(items)
        self._choice = 0

        width = max(len(item) for item in self._items)
        height = len(self._items)

        self._min = min(3, height), min(3, width) + 4
        self._def = height, width + 4

    def render(self, cells: _np.ndarray) -> None:

        rows, cols = cells.shape
        lines = _np.ndarray((rows,), dtype=f'=U{cols}', buffer=cells)

        count = min(len(self._items), rows)
        choice = self._choice - 1

        for y, item in enumerate(self._items[:count]):

            text = f" {item:.{cols-4}} "

            if y == choice:
                lines[y] = text.center(cols, '=')
            else:
                lines[y] = text.center(cols)

        lines[count:] = ''

        self._needs_refresh = False

    def handle_event(self, event: _events.Event) -> bool:

        if not isinstance(event, _events.VerticalNavEvent):

            return False

        if not 0 <= self._choice <= len(self._items):

            self._choice = 0

        self._choice += event.y
        self._choice %= len(self._items) + 1

        self.invalidate()

        return True

    def get_choice(self) -> _Optional[int]:

        if not 0 < self._choice <= len(self._items):

            return None

        return self._choice - 1
