import pygame as pg
from .escapes import EscapeCodeProcessor, NotEscapeCodeError, ParserError
from .cursor import Cursor, COL_SIZE

DISABLE_ESCAPE_CODES: bool = False


class Console:
    def __init__(self, font: pg.font.Font, surface: pg.surface.Surface) -> None:
        self.cursor = Cursor()
        self.font = font
        self.surface = surface
        self._prepare_console()
        self.cursor.state.max_cols = self.get_max_cols()

    def get_max_cols(self) -> int:
        w, _ = self.surface.get_size()

        return w // COL_SIZE

    def _prepare_console(self) -> None:
        self.surface.fill(pg.color.Color(0, 0, 0))

    def output(self, string: str) -> None:
        i = 0
        while i < len(string):
            try:
                if DISABLE_ESCAPE_CODES:
                    raise NotImplementedError

                esc = EscapeCodeProcessor(string[i:], self.cursor)
            except NotEscapeCodeError:
                # Print normal printable char
                self.put_char(string[i])
                i += 1
            except (NotImplementedError, ParserError):
                # Error during parsing escape, skip escape byte and
                # print rest of the sequence
                self.put_char(string[i])
                i += 1
            else:
                # Escape sequence processed successfully.
                # skip processed sequence
                i += esc.chars_to_skip

    def put_char(self, char: str) -> None:
        char_surf = self.font.render(
            char, True, self.cursor.state.fg, self.cursor.state.bg
        )
        self.surface.blit(char_surf, self.cursor.cell_px_position)
        self.cursor.next()
