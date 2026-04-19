import logging
import time
from contextlib import contextmanager


@contextmanager
def timing(message: str = None) -> int:
    start = time.perf_counter_ns()
    try:
        yield start
    finally:
        end = time.perf_counter_ns()
        dur = end - start
        micros = dur // 1000
        if micros < 10_000_000:
            t = f'{micros:,d}'
        else:
            seconds = micros / 1_000_000
            t = f'{seconds:,.2f}s'
        logging.info(f"[{t:>9s}] {message}")
