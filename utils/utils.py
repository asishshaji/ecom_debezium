from functools import wraps
import time
import asyncio
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def timeit(func: Callable[P, T]) -> Callable[P, T]:
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_timeit_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            print(f"Async function {func.__name__} took {total_time:.10f} seconds")
            return result

        return async_timeit_wrapper  # type: ignore
    else:

        @wraps(func)
        def sync_timeit_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            print(f"Function {func.__name__} took {total_time:.10f} seconds")
            return result

        return sync_timeit_wrapper  # type: ignore
