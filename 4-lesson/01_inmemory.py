import time
from typing import Any, Optional
from datetime import datetime, timedelta


class InMemoryCache:
    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        expires_at = time.time() + ttl
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
    
    def get(self, key: str) -> Any:
        if key not in self._cache:
            return None
        
        entry = self._cache[key]

        if time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        
        if time.time() > entry['expires_at']:
            del self._cache[key]
            return False
        
        return True
    
    def clear(self) -> None:
        self._cache.clear()
    
    def cleanup(self) -> int:
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        self.cleanup()
        return len(self._cache)
    
    def get_ttl(self, key: str) -> Optional[float]:
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        remaining = entry['expires_at'] - time.time()
        
        if remaining <= 0:
            del self._cache[key]
            return None
        
        return remaining


if __name__ == "__main__":
    cache = InMemoryCache()
    
    cache.set("user:1", {"name": "Alice", "age": 30}, ttl=10)
    cache.set("user:2", {"name": "Bob", "age": 25}, ttl=5)
    cache.set("session:abc123", "active", ttl=3)
    
    print("Immediately after adding:")
    print(f"user:1 = {cache.get('user:1')}")
    print(f"user:2 = {cache.get('user:2')}")
    print(f"session:abc123 = {cache.get('session:abc123')}")
    print(f"Cache size: {cache.size()}")
    
    # Wait 4 seconds
    print("\nWaiting 4 seconds...")
    time.sleep(4)
    
    print("\nAfter 4 seconds:")
    print(f"user:1 = {cache.get('user:1')}")
    print(f"user:2 = {cache.get('user:2')}")
    print(f"session:abc123 = {cache.get('session:abc123')} (expired)")
    print(f"TTL for user:1: {cache.get_ttl('user:1'):.2f} seconds")

