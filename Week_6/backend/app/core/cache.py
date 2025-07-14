import redis
import json
import time
import os
from typing import Any, Optional, Callable

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

_redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

CACHE_METRICS = {
    'hits': 0,
    'misses': 0,
    'sets': 0,
    'invalidations': 0,
    'last_reset': time.time()
}

CACHE_DEFAULT_TTL = 3600  # 1 hour

class Cache:
    @staticmethod
    def get(key: str) -> Optional[Any]:
        value = _redis.get(key)
        if value is not None:
            CACHE_METRICS['hits'] += 1
            try:
                return json.loads(value)
            except Exception:
                return value
        else:
            CACHE_METRICS['misses'] += 1
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = CACHE_DEFAULT_TTL):
        CACHE_METRICS['sets'] += 1
        _redis.setex(key, ttl, json.dumps(value))

    @staticmethod
    def invalidate(key: str):
        CACHE_METRICS['invalidations'] += 1
        _redis.delete(key)

    @staticmethod
    def warm(key: str, fetch_func: Callable[[], Any], ttl: int = CACHE_DEFAULT_TTL):
        value = fetch_func()
        Cache.set(key, value, ttl)
        return value

    @staticmethod
    def get_or_set(key: str, fetch_func: Callable[[], Any], ttl: int = CACHE_DEFAULT_TTL):
        value = Cache.get(key)
        if value is not None:
            return value
        value = fetch_func()
        Cache.set(key, value, ttl)
        return value

    @staticmethod
    def metrics():
        now = time.time()
        elapsed = now - CACHE_METRICS['last_reset']
        return {
            'hits': CACHE_METRICS['hits'],
            'misses': CACHE_METRICS['misses'],
            'sets': CACHE_METRICS['sets'],
            'invalidations': CACHE_METRICS['invalidations'],
            'hit_rate': CACHE_METRICS['hits'] / max(1, (CACHE_METRICS['hits'] + CACHE_METRICS['misses'])),
            'miss_rate': CACHE_METRICS['misses'] / max(1, (CACHE_METRICS['hits'] + CACHE_METRICS['misses'])),
            'uptime_seconds': elapsed
        }

    @staticmethod
    def reset_metrics():
        CACHE_METRICS['hits'] = 0
        CACHE_METRICS['misses'] = 0
        CACHE_METRICS['sets'] = 0
        CACHE_METRICS['invalidations'] = 0
        CACHE_METRICS['last_reset'] = time.time() 