"""
Cache Service - Redis for performance optimization
"""
import logging
import json
import hashlib
from typing import Any, Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis cache service for performance optimization
    Caches:
    - Embedding vectors
    - Query results
    - LLM responses (for identical queries)
    """

    def __init__(self):
        self.redis_client = None
        self.use_mock = True
        self.mock_cache = {}

    def initialize(self, redis_url: Optional[str] = None):
        """Initialize Redis connection"""
        try:
            import redis
            from app.config import settings

            url = redis_url or (settings.redis_url if hasattr(settings, 'redis_url') else None)

            if not url:
                logger.info("Redis not configured. Using in-memory cache.")
                return

            self.redis_client = redis.from_url(url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.use_mock = False
            logger.info("Redis cache initialized")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.info("Using in-memory cache instead")
            self.use_mock = True

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.use_mock:
                value = self.mock_cache.get(key)
                if value and value.get('expires_at', float('inf')) > time.time():
                    return value.get('data')
                return None

            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (seconds)"""
        try:
            if self.use_mock:
                self.mock_cache[key] = {
                    'data': value,
                    'expires_at': time.time() + ttl
                }
                return True

            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self.use_mock:
                self.mock_cache.pop(key, None)
                return True

            self.redis_client.delete(key)
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_string = json.dumps({
            'args': args,
            'kwargs': kwargs
        }, sort_keys=True, ensure_ascii=False)

        return hashlib.md5(key_string.encode()).hexdigest()

    def cache_embedding(self, text: str, embedding: list, ttl: int = 86400):
        """Cache embedding vector (24 hour TTL)"""
        key = f"embedding:{self.generate_key(text)}"
        return self.set(key, embedding, ttl)

    def get_cached_embedding(self, text: str) -> Optional[list]:
        """Get cached embedding"""
        key = f"embedding:{self.generate_key(text)}"
        return self.get(key)

    def cache_query_result(self, query: str, result: Any, ttl: int = 1800):
        """Cache query result (30 minute TTL)"""
        key = f"query:{self.generate_key(query)}"
        return self.set(key, result, ttl)

    def get_cached_query_result(self, query: str) -> Optional[Any]:
        """Get cached query result"""
        key = f"query:{self.generate_key(query)}"
        return self.get(key)

    def clear_all(self):
        """Clear all cache (use with caution)"""
        if self.use_mock:
            self.mock_cache.clear()
        else:
            self.redis_client.flushdb()


def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results

    Usage:
        @cache_result(ttl=3600, key_prefix="my_function")
        def my_function(arg1, arg2):
            # expensive operation
            return result
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = cache_service

            # Generate cache key
            key = f"{key_prefix or func.__name__}:{cache.generate_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss: {key} - stored result")

            return result

        return wrapper

    return decorator


# Global instance
cache_service = CacheService()
