#!/usr/bin/env python3

from . import ez_dialog, Choice, Console


def _main():
    import time

    print("Das Lamm sagt Hurz!", end='', flush=True)

    time.sleep(0.5)

    console = Console()

    ez_dialog(Choice(["1", "wunschvorstellung", "3", "4", "fünf", "sechs"]), console=console)

    time.sleep(1)
    ez_dialog(Choice(["foo", "bar", "foobar", "baz"]), console=console)

    time.sleep(1)
    ez_dialog(Choice(["1", "wunschvorstellung", "3", "4", "fünf", "sechs", "sieben", "acht"]), console=console)

    time.sleep(1)
    ez_dialog(Choice(["hundert", "foo", "bar"]), console=console)


_main()
