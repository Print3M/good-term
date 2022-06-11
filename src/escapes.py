from .colors import SGR_BRIGHT_COLORS, SGR_COLORS
from .cursor import Cursor
import enum
import pygame as pg


class ControlCodes(enum.Enum):
    BEL = "\x07"
    BS = "\x08"
    HT = "\x09"
    LF = "\x0A"
    FF = "\x0C"
    CR = "\x0D"
    ESC = "\x1B"

    @classmethod
    def values(cls):
        return tuple([memb.value for memb in cls.__members__.values()])


class FeEscapeSeq(enum.Enum):
    SS2 = "N"
    SS3 = "O"
    DCS = "P"
    CSI = "["
    ST = "\\"
    OSC = "]"
    SOS = "X"
    PM = "^"
    APC = "_"


class ParserError(Exception):
    pass


class NotEscapeCodeError(Exception):
    pass


class EscapeCodeProcessor:
    """
    Read more:
        https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    def __init__(self, string: str, cursor: Cursor) -> None:
        """
        :string - entire string to process
        """
        self.chars_to_skip: int = 0

        # Check if it is escape sequence
        if string.startswith(ControlCodes.values()) == False:
            # Raise error if char is not in escape byte
            # We want to process only legit ANSI escape codes here!
            raise NotEscapeCodeError

        self.chars_to_skip += 1  # Always skip non-printable escape code
        self.string = string
        self.cursor = cursor

        match string[0]:
            case ControlCodes.BS.value:
                self.cursor.bs()
            case ControlCodes.HT.value:
                self.cursor.ht()
            case ControlCodes.BEL.value:
                self.cursor.bs()
            case ControlCodes.LF.value:
                self.cursor.lf()
            case ControlCodes.CR.value:
                self.cursor.cr()
            case ControlCodes.ESC.value:
                self._parse_esc()
            case _:
                raise NotImplementedError

    def _parse_esc(self):
        match self.string[1]:
            case FeEscapeSeq.CSI.value:
                CsiProcessor(self.string[2:], self.cursor, self)
            case FeEscapeSeq.OSC.value:
                OscProcessor(self.string[2:], self)
            case _:
                raise NotImplementedError


class CsiProcessor:
    def __init__(self, string: str, cursor: Cursor, main: EscapeCodeProcessor) -> None:
        self.main = main
        self.cursor = cursor
        self.terminators = {"m": self.sgr_handler}
        terminator = self.get_terminator(string)

        if terminator is None:
            raise NotImplementedError

        self.args = string[: string.find(terminator)]
        self.main.chars_to_skip += len(self.args) + 2  # + start and end terminator
        handler = self.terminators.get(terminator)

        if handler is None:
            raise NotImplementedError

        handler()

    def get_terminator(self, string: str) -> str | None:
        for char in string:
            if ord(char) >= ord("A") and ord(char) <= ord("~"):
                return char

        return None

    def sgr_handler(self) -> None:
        """
        Only decimal args separated by semicolons are allowed.
        """
        try:
            args = [int(arg) for arg in self.args.split(";")]
        except:
            raise ParserError

        for arg in args:
            match arg:
                case 0:
                    self.cursor.sgr_reset()
                case 1:
                    self.cursor.state.bold = True
                case 3:
                    self.cursor.state.italic = True
                case arg if arg in range(30, 37):
                    color = arg - 30
                    self.cursor.state.fg = SGR_COLORS[color]
                case arg if arg in range(40, 47):
                    color = arg - 40
                    self.cursor.state.bg = SGR_COLORS[color]
                case arg if arg in range(90, 97):
                    color = arg - 90
                    self.cursor.state.fg = SGR_BRIGHT_COLORS[color]
                case arg if arg in range(100, 107):
                    color = arg - 100
                    self.cursor.state.bg = SGR_BRIGHT_COLORS[color]


class OscProcessor:
    terminator = ControlCodes.BEL.value

    def __init__(self, string: str, main: EscapeCodeProcessor) -> None:
        self.main = main
        args = self._extract_args(string)

        match args[0]:
            case "0":
                self._change_window_caption(args)
            case _:
                raise NotImplementedError

    def _extract_args(self, string: str) -> list[str]:
        idx = string.find(self.terminator)

        if idx == -1:
            raise ParserError

        raw_args = string[:idx]
        self.main.chars_to_skip += len(raw_args) + 2  # + terminator
        args = raw_args.split(";")

        if len(args) == 0:
            raise ParserError

        return args

    def _change_window_caption(self, args: list[str]) -> None:
        if len(args) != 2:
            raise ParserError

        pg.display.set_caption(args[1])
