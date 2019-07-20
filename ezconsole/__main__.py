#!/usr/bin/env python3

import asyncio
import logging
import sys

from . import ez_dialog, Choice, Console


if __debug__ or sys.flags.dev_mode:
    logging.basicConfig(level=logging.DEBUG)


async def _main():

    loop = asyncio.get_running_loop()
    logging.debug("loop = %r", loop)

    print("Das Lamm sagt Hurz!", end='', flush=True)

    await asyncio.sleep(0.5)

    console = Console()

    ez_dialog(Choice(["1", "wunschvorstellung", "3", "4", "fünf", "sechs"]), console=console)

    await asyncio.sleep(1)
    ez_dialog(Choice(["foo", "bar", "foobar", "baz"]), console=console)

    await asyncio.sleep(1)
    ez_dialog(Choice(["1", "wunschvorstellung", "3", "4", "fünf", "sechs", "sieben", "acht"]), console=console)

    await asyncio.sleep(1)
    ez_dialog(Choice(["hundert", "foo", "bar"]), console=console)

    console.close()

    await asyncio.sleep(0.5)


asyncio.run(_main())
