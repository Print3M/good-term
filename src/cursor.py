from dataclasses import dataclass
import pygame as pg
from .colors import TRANSPARENT, WHITE


y_px = int
x_px = int
px_position = tuple[x_px, y_px]
px_size = tuple[x_px, y_px]

COL_SIZE = 10
ROW_SIZE = 16


@dataclass
class CursorState:
    max_cols: int = 80
    cols: int = 0
    rows: int = 0
    fg: pg.color.Color = WHITE
    bg: pg.color.Color = TRANSPARENT
    bold: bool = False
    italic: bool = False


class Cursor:
    state = CursorState()

    @property
    def cell_position(self) -> tuple[int, int]:
        return self.state.cols, self.state.rows

    @property
    def cell_px_position(self) -> px_position:
        # Get position of top right pixel of cell
        # TODO: Remove this consts, it depends on main font size!
        return self.state.cols * COL_SIZE, self.state.rows * ROW_SIZE

    def gotoxy(self, cols: int, rows: int) -> None:
        self.state.cols = cols
        self.state.rows = rows

    def next(self) -> None:
        if self.state.cols < self.state.max_cols - 1:
            self.state.cols += 1
        else:
            self.lf()
            self.cr()

    def cr(self) -> None:
        self.state.cols = 0

    def lf(self) -> None:
        self.state.rows += 1

    def go_left(self) -> None:
        if self.state.cols > 0:
            self.state.cols -= 1
        else:
            # Go to previous line
            if self.state.rows > 0:
                self.state.rows -= 1
                self.state.cols = self.state.max_cols - 1

    def go_right(self) -> None:
        self.next()

    def bs(self) -> None:
        self.go_left()

    def ht(self) -> None:
        """
            Tab = 4 spaces.
        """
        for _ in range(4):
            self.next()

    def sgr_reset(self):
        self.state.fg = WHITE
        self.state.bg = TRANSPARENT
        self.state.bold = False
        self.state.italic = False
