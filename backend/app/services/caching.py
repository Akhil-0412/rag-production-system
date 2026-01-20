import redis
import json
import hashlib
from typing import Optional, Dict
from app.config import settings

class CacheService:
    def __init__(self):
        self.enabled = False
        self.redis = None
        
        if settings.REDIS_URL:
            try:
                self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
                self.redis.ping()
                self.enabled = True
                print("Redis Cache connected.")
            except Exception as e:
                print(f"Redis connection failed: {e}. Caching disabled.")
        else:
            print("REDIS_URL not set. Caching disabled.")

    def _generate_key(self, query: str) -> str:
        """Generate a consistent cache key for a query."""
        # Normalize: lower case, strip whitespace
        normalized = query.strip().lower()
        return f"rag_cache:{hashlib.sha256(normalized.encode()).hexdigest()}"

    def get_cached_response(self, query: str) -> Optional[Dict]:
        if not self.enabled:
            return None
            
        key = self._generate_key(query)
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
            
        return None

    def set_cached_response(self, query: str, response: Dict, ttl: int = 3600):
        if not self.enabled:
            return
            
        key = self._generate_key(query)
        try:
            self.redis.setex(key, ttl, json.dumps(response))
        except Exception as e:
            print(f"Cache set error: {e}")
