import logging
import time
from functools import wraps

from taxi_manager.infrastructure.cache_manager.services import CacheManager

cache_manager = CacheManager()

logger = logging.getLogger(__name__)


def cached_method(key_fn, timeout=None):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            key = key_fn(*args, **kwargs)

            start = time.perf_counter()
            value = cache_manager.get(key)
            elapsed = time.perf_counter() - start

            if not cache_manager.is_missing(value):
                logger.info("Cache get HIT key=%s: %.3f ms", key, elapsed * 1000)
                return value

            logger.info("Cache get MISS key=%s: %.3f ms", key, elapsed * 1000)

            start = time.perf_counter()
            value = method(self, *args, **kwargs)
            value_load_elapsed = time.perf_counter() - start

            logger.info("Value load key=%s: %.3f ms", key, value_load_elapsed * 1000)

            cache_manager.set(key, value, timeout=timeout)

            return value

        return wrapper

    return decorator
