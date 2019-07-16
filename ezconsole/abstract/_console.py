#!/usr/bin/env python3


class _Console:

    def print(self, s: str, flush: bool = False) -> None:
        raise NotImplementedError

    def get_width(self) -> int:
        raise NotImplementedError

    def get_height(self) -> int:
        raise NotImplementedError

    def get_colors(self) -> int:
        return 2

    def request_size(self, height: int) -> int:
        raise NotImplementedError

    def line_at(self, y: int, text: str, tail: int = 0) -> None:
        raise NotImplementedError
