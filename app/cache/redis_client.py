import json
import redis
from typing import Optional, Dict, Any, List
from app.config import Config

class RedisClient:
    def __init__(self):
        # Connection to master (for writes)
        self.master = redis.Redis(
            host=Config.REDIS_MASTER_HOST,
            port=Config.REDIS_MASTER_PORT,
            decode_responses=True
        )
        
        # Connections to replicas (for reads)
        self.replicas = [
            redis.Redis(host=Config.REDIS_REPLICA_1_HOST, port=Config.REDIS_REPLICA_1_PORT, decode_responses=True),
            redis.Redis(host=Config.REDIS_REPLICA_2_HOST, port=Config.REDIS_REPLICA_2_PORT, decode_responses=True)
        ]
        
        # Default expiration time for cache items (30 minutes)
        self.default_expiry = Config.CACHE_TTL
    
    def _get_replica(self) -> redis.Redis:
        """Get a replica connection using a simple round-robin strategy"""
        import random
        return random.choice(self.replicas)
    
    def set_data(self, key: str, data: Any, expiry: Optional[int] = None) -> None:
        """Store data in Redis master with optional expiry time"""
        serialized = json.dumps(data)
        self.master.set(key, serialized, ex=expiry or self.default_expiry)
    
    def get_data(self, key: str) -> Optional[Any]:
        """Get data from a Redis replica"""
        replica = self._get_replica()
        data = replica.get(key)
        if data:
            return json.loads(data)
        return None
    
    def delete_data(self, key: str) -> None:
        """Delete data from Redis"""
        self.master.delete(key)
    
    def increment_counter(self, key: str, field: str, amount: int = 1) -> None:
        """Increment a hash field value by the given amount"""
        self.master.hincrby(key, field, amount)
    
    def get_top_values(self, key: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get the top N values from a Redis hash, sorted by value"""
        replica = self._get_replica()
        all_items = replica.hgetall(key)
        if not all_items:
            return []
        
        # Convert values to integers and sort
        sorted_items = sorted(
            [(k, int(v)) for k, v in all_items.items()], 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top N
        return [{"id": item[0], "count": item[1]} for item in sorted_items[:count]]
    
    def is_connected(self) -> bool:
        """Check if Redis master is connected"""
        try:
            return self.master.ping()
        except:
            return False

# Global Redis client instance
redis_client = RedisClient() 