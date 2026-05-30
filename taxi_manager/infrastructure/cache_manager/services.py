from django.core.cache import cache

from taxi_manager.raw_application.chat_bot.interfaces import ICacheManager


class CacheManager(ICacheManager):
    def get(self, key: str, default=None):
        return cache.get(key, default=default)
    
    def set(self, key: str, value: any, timeout=None):
        return cache.set(key, value, timeout=timeout)
    

