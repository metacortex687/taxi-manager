import time
from functools import wraps

from taxi_manager.infrastructure.cache_manager.services import CacheManager

cache_manager = CacheManager()


def cached_method(key_fn, timeout=None):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            key = key_fn(*args, **kwargs)

            start = time.perf_counter()
            value = cache_manager.get(key)
            elapsed = time.perf_counter() - start

            if not cache_manager.is_missing(value):
                print(f"Cache get HIT key={key}: {elapsed * 1000:.3f} ms")
                return value

            print(f"Cache get MISS key={key}: {elapsed * 1000:.3f} ms")

            if not cache_manager.is_missing(value):
                return value
            
            start = time.perf_counter()
            value = method(self, *args, **kwargs)
            value_load_elapsed = time.perf_counter() - start

            print(f"Value load key={key}: {value_load_elapsed * 1000:.3f} ms")

            cache_manager.set(key, value, timeout=timeout)

            return value

        return wrapper

    return decorator
