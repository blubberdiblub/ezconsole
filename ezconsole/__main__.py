#!/usr/bin/env python3

import asyncio
import logging
import sys

from . import Choice, Console, GUI


if __debug__ or sys.flags.dev_mode:
    logging.basicConfig(level=logging.DEBUG)

    _loop = asyncio.get_event_loop()
    _loop.slow_callback_duration = 0.02

    logging.debug("loop = %r @%#x", _loop, id(_loop))
    del _loop


async def _main():

    __loop = asyncio.get_running_loop()
    logging.debug("loop = %r @%#x", __loop, id(__loop))

    await asyncio.sleep(0.1)

    print("Das Lamm sagt Hurz!", end='', flush=True)

    await asyncio.sleep(0.1)

    console = Console()
    element = Choice(["1", "wunschvorstellung", "3", "4", "fünf", "sechs"])
    gui = GUI(element, console=console)

    await gui.handle()

    print('', flush=True)

    console.close()

    await asyncio.sleep(0.1)


loop = asyncio.get_event_loop()
logging.debug("loop = %r @%#x", loop, id(loop))
loop.run_until_complete(_main())

pending_tasks = asyncio.all_tasks(loop)
if pending_tasks:

    for task in pending_tasks:

        logging.debug("pending task: %s", task)
        task.cancel()

    loop.run_until_complete(asyncio.gather(*pending_tasks, loop=loop,
                                           return_exceptions=True))

    for task in pending_tasks:

        if task.cancelled():
            continue

        exception = task.exception()
        if exception is not None:
            logging.exception("pending exception: %s", exception,
                              exc_info=(type(exception), exception,
                                        exception.__traceback__))

loop.run_until_complete(loop.shutdown_asyncgens())
asyncio.set_event_loop(None)
loop.close()
