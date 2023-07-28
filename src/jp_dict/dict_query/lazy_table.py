import threading
from typing import Any
from collections.abc import Callable

TIMEOUT = 30 * 60  # 30 mins

LoadFunc = Callable[[], dict[int, Any]]


class Timer:
    """wrapper class for threading.Timer"""

    def __init__(self, timeout: int | float, callback: Callable) -> None:
        self.callback = callback
        self.timeout = timeout

    def start(self) -> None:
        self.cancel()
        self._timer = threading.Timer(self.timeout, self._stop)
        self._timer.daemon = True
        self._timer.start()

    def cancel(self) -> None:
        try:
            self._timer.cancel()
            del self._timer
        except AttributeError:
            pass

    def _stop(self) -> None:
        self.cancel()
        self.callback()


class LazyTable:
    """lazy-load tables and automatically unload them when not in use"""

    def __init__(self, load_func: LoadFunc) -> None:
        self._load_func = load_func
        self._timer = Timer(TIMEOUT, self._unload)

    @property
    def contents(self) -> dict[int, Any]:
        self._timer.cancel()  # manually cancel to avoid race condition
        if not hasattr(self, "_contents"):
            self._contents = self._load_func()
        self._timer.start()
        return self._contents

    def _unload(self) -> None:
        try:
            del self._contents
        except AttributeError:
            pass
