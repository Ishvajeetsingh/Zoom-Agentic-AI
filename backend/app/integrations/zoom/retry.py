import time
from collections.abc import Callable
from typing import TypeVar

import httpx

T = TypeVar("T")


def retry_sync(
    operation: Callable[[], T],
    *,
    attempts: int,
    backoff_seconds: float,
    retry_on_status: set[int] | None = None,
) -> T:
    retry_on_status = retry_on_status or set()
    last_error: Exception | None = None

    for attempt in range(1, max(attempts, 1) + 1):
        try:
            result = operation()
            if isinstance(result, httpx.Response) and result.status_code in retry_on_status:
                if attempt == attempts:
                    return result
                time.sleep(backoff_seconds * attempt)
                continue
            return result
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as exc:
            last_error = exc
            if attempt == attempts:
                raise
            time.sleep(backoff_seconds * attempt)

    if last_error:
        raise last_error
    return operation()
