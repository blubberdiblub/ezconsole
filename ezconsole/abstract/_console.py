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
