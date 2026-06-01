import time

class timer:
    def __init__(self):
        self._start = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    @property
    def ms(self):
        if self._start is None:
            return None
        return (time.perf_counter() - self._start) * 1000

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f"exception with time perf counter: {exc_value}")
        return False

