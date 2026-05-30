from django.core.cache import cache

from taxi_manager.raw_application.chat_bot.interfaces import ICacheManager

from django.conf import settings

CACHE_ENABLED = settings.CACHE_ENABLED

class CacheManager(ICacheManager):
    MISSING = object()

    def get(self, key: str):
        if not CACHE_ENABLED:
            return self.MISSING
        
        value = cache.get(key, default=self.MISSING)
        
        return value
    
    def set(self, key: str, value: any, timeout=None):
        if not CACHE_ENABLED:
            return

        return cache.set(key, value, timeout=timeout)
    
    def is_missing(self, value: any):
        if not CACHE_ENABLED:
            return True
        
        return value is self.MISSING
    

    

