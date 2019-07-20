#!/usr/bin/env python3

from typing import (
    Any as _Any,
    Callable as _Callable,
)

from abc import (
    ABCMeta as _ABCMeta,
    abstractmethod as _abstractmethod,
)


class _Console(metaclass=_ABCMeta):

    @_abstractmethod
    def close(self, timeout: float = 0.1) -> None:
        raise NotImplementedError

    @_abstractmethod
    def print(self, s: str, flush: bool = False) -> None:
        raise NotImplementedError

    @_abstractmethod
    def get_width(self) -> int:
        raise NotImplementedError

    @_abstractmethod
    def get_height(self) -> int:
        raise NotImplementedError

    def get_colors(self) -> int:
        return 2

    @_abstractmethod
    def request_size(self, height: int) -> int:
        raise NotImplementedError

    @_abstractmethod
    def line_at(self, y: int, text: str, tail: int = 0) -> None:
        raise NotImplementedError

    @_abstractmethod
    def register_input_callback(self, callback: _Callable) -> _Any:
        raise NotImplementedError

    @_abstractmethod
    def unregister_input_callback(self, token: _Any) -> None:
        raise NotImplementedError
