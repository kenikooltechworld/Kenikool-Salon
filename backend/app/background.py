"""Background task runner without Celery."""

import asyncio
import logging
from functools import partial
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for running sync functions in background
_executor = ThreadPoolExecutor(max_workers=10)


def run_in_background(func, *args, **kwargs):
    """Run a sync or async function in the background without waiting for result."""
    if asyncio.iscoroutinefunction(func):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(func(*args, **kwargs))
    else:
        _executor.submit(func, *args, **kwargs)
