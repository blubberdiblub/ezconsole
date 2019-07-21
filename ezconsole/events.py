#!/usr/bin/env python3

from abc import (
    ABCMeta as _ABCMeta,
    abstractproperty as _abstractproperty,
)


class Event(metaclass=_ABCMeta):

    pass


class QuitEvent(Event):

    pass


class NavigateEvent(Event):

    @_abstractproperty
    def x(self) -> int:
        raise NotImplementedError

    @_abstractproperty
    def y(self) -> int:
        raise NotImplementedError

    def __setattr__(self, key, value):
        raise AttributeError("not writable")


class VerticalNavEvent(NavigateEvent):

    x = 0


class HorizontalNavEvent(NavigateEvent):

    y = 0


class UpNavEvent(VerticalNavEvent):

    y = -1


class DownNavEvent(VerticalNavEvent):

    y = 1


class LeftNavEvent(HorizontalNavEvent):

    x = -1


class RightNavEvent(HorizontalNavEvent):

    x = 1


if __name__ == '__main__':

    def _main():

        import logging

        logging.basicConfig(level=logging.DEBUG)

        ev = Event()
        logging.debug("%r", ev)
        logging.debug("%r", ev.__class__.__mro__)

        ev = UpNavEvent()
        logging.debug("%r", ev)
        logging.debug("%r", ev.__class__.__mro__)
        logging.debug("(%d, %d)", ev.x, ev.y)

        ev = DownNavEvent()
        logging.debug("%r", ev)
        logging.debug("%r", ev.__class__.__mro__)
        logging.debug("(%d, %d)", ev.x, ev.y)

    _main()
