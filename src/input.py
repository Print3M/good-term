from .pty import Master
import pygame as pg

class InputKeyProcessor:
    def __init__(self, master: Master):
        self.master = master

    def process(self, event: pg.event.Event) -> None:
        if hasattr(event, "unicode") == False:
            return

        self.master.write(event.unicode)
