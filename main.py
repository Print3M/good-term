import sys
import os
import threading
from src.pty import Master, Slave, get_pty
from src.console import Console
from src.input import InputKeyProcessor
import pygame as pg

W_WIDTH = 750
W_HEIGHT = 500


def output_worker(master: Master, console: Console) -> None:
    # Trzeba zrobić wielowątkowo, bo output może być przetwarzany
    # przez kilka sekund, a chcemy móc zastopować wtedy proces (wysłać
    # ctrl+c na mastera)
    while True:
        if master.is_waiting(25):
            data = master.read()
            console.output(data)



def child_process(master: Master, slave: Slave) -> None:
    # TODO: Error checking
    del master
    os.dup2(slave.fd, 0)
    os.dup2(slave.fd, 1)
    os.dup2(slave.fd, 2)
    del slave
    os.execv("/bin/bash", ["bash"])


if __name__ == "__main__":
    master, slave = get_pty()
    pid = os.fork()

    if pid == 0:
        child_process(master, slave)

    # Parent process
    pg.init()
    surface = pg.display.set_mode(size=(W_WIDTH, W_HEIGHT))
    pg.font.init()
    font = pg.font.SysFont("Monospace", size=16, bold=False, italic=False)
    console = Console(font=font, surface=surface)
    key = InputKeyProcessor(master)

    worker = threading.Thread(target=output_worker, args=(master, console), daemon=True)
    worker.start()

    while 1:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    pg.quit()
                    sys.exit()
                case pg.KEYDOWN:
                    key.process(event)

        pg.display.update()
