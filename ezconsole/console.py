#!/usr/bin/env python3

from typing import Tuple as _Tuple

import numpy as _np

from .abstract import Console as _AbstractConsole


class Console:

    def __init__(self) -> None:

        self._abstract_console = _AbstractConsole()
        cols = self._abstract_console.get_width()

        self._prev_cells = _np.zeros((0, cols), dtype='=U1')
        self._cells = _np.zeros((0, cols), dtype='=U1')

    def visible_dims(self) -> _Tuple[int, int]:

        return self._abstract_console.get_height(), self._abstract_console.get_width()

    def resize_buffer(self, rows, cols) -> None:

        if (rows, cols) == self._cells.shape:
            return

        try:
            self._cells.resize((rows, cols))

        except ValueError:
            pass

        else:
            return

        old_rows, old_cols = self._cells.shape

        if rows <= old_rows and cols <= old_cols:
            self._cells = self._cells[:rows, :cols]

        else:
            new_cells = _np.zeros((rows, cols), dtype=self._cells.dtype)
            new_cells[:old_rows, :old_cols] = self._cells[:rows, :cols]
            self._cells = new_cells

    def flush(self) -> None:

        if _np.array_equal(self._cells, self._prev_cells):
            return

        prev_rows, prev_cols = self._prev_cells.shape
        rows, cols = self._cells.shape

        if rows != prev_rows:
            n = self._abstract_console.request_size(rows)
            if n != rows:
                rows = n

                try:
                    self._cells.resize((rows, cols))

                except ValueError:
                    self._cells = self._cells[:rows]

        prev_lines = _np.ndarray((prev_rows,),
                                 dtype=f'=U{prev_cols}',
                                 buffer=self._prev_cells)
        lines = _np.ndarray((rows,), dtype=f'=U{cols}', buffer=self._cells)
        indices, = (lines[:prev_rows] != prev_lines[:rows]).nonzero()

        if len(indices):
            for i, line, old_len in zip(indices, lines[indices],
                                        _np.char.str_len(prev_lines[indices])):

                self._abstract_console.line_at(i, line, max(old_len - len(line), 0))

        if rows > prev_rows:
            for i in range(prev_rows, rows):
                self._abstract_console.line_at(i, lines[i], 0)

        if self._prev_cells.shape == self._cells.shape:
            self._prev_cells[:] = self._cells

        else:
            self._prev_cells = self._cells.copy()

    def get_buffer(self) -> _np.ndarray:

        return self._cells
