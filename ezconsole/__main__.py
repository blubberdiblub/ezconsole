#!/usr/bin/env python3

from . import ez_dialog, Choice


def _main():
    import time

    print("Das Lamm sagt Hurz!")

    time.sleep(0.5)

    ez_dialog(Choice(["foo", "bar", "foobar", "baz"]))


_main()
