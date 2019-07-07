#!/usr/bin/env python3

from .abstract import Console


def _main():
    import time

    print("foobar")

    time.sleep(0.5)

    console = Console()

    width = console.get_width()
    height = console.get_height()
    colors = console.get_colors()

    console.print(f"{width} x {height}, {colors} colors", flush=True)

    time.sleep(3)


_main()
