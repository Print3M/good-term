import ctypes
import sys
import os
import select

libc = ctypes.CDLL("libc.so.6")

master_fd = int
slave_fd = int


class Slave:
    def __init__(self, master: master_fd) -> None:
        slave_path = self.get_path(master)
        self.fd = self.open(slave_path)

    def __del__(self) -> None:
        os.close(self.fd)

    @staticmethod
    def get_path(master: master_fd) -> str:
        # Get path of slave device
        slave_buf = ctypes.create_string_buffer(256)

        if libc.ptsname_r(master, slave_buf, 256) != 0:
            sys.exit("ptsname_r() error")

        return slave_buf.value.decode("ascii")

    @staticmethod
    def open(slave_path: str) -> slave_fd:
        return os.open(slave_path, flags=os.O_RDWR)

    def write(self, val: str) -> None:
        os.write(self.fd, val.encode("ascii"))

    def read(self) -> bytes:
        return os.read(self.fd, 1024)


class Master:
    _ptmx_path = "/dev/ptmx"

    def __init__(self) -> None:
        self.fd = self.open()
        libc.grantpt(self.fd)
        libc.unlockpt(self.fd)

        # Register poll for future
        self._poll_obj = select.poll()
        self._poll_obj.register(self.fd)

    def __del__(self) -> None:
        os.close(self.fd)

    @classmethod
    def open(cls) -> master_fd:
        return os.open(cls._ptmx_path, flags=os.O_RDWR)

    def write(self, val: str) -> None:
        os.write(self.fd, val.encode("ascii"))

    def read(self) -> str:
        return os.read(self.fd, 1024).decode("ascii")

    def is_waiting(
        self,
        timeout_ms: int,
    ) -> bool:
        """
        Check if there is something to read from master fd.
        """
        data = self._poll_obj.poll(timeout_ms)

        if len(data) == 0:
            return False

        fd, event = data[0]

        if fd != self.fd:
            return False

        return event & select.POLLIN


def get_pty() -> tuple[Master, Slave]:
    master = Master()
    slave = Slave(master.fd)

    return master, slave
