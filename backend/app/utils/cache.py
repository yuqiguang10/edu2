import json
import redis
from typing import Any, Optional, Union
from functools import wraps
from app.core.config import settings

# Redis客户端
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    key_parts = []
    
    # 添加位置参数
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # 添加关键字参数
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cache(expire: int = 300, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            try:
                cached_result = redis_client.get(cache_key_str)
                if cached_result:
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            try:
                redis_client.setex(
                    cache_key_str,
                    expire,
                    json.dumps(result, default=str)
                )
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
            
            return result
        
        return wrapper
    return decorator


class CacheManager:
    """缓存管理器"""
    
    @staticmethod
    def set(key: str, value: Any, expire: int = 300) -> bool:
        """设置缓存"""
        try:
            return redis_client.setex(
                key, 
                expire, 
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    @staticmethod
    def delete(key: str) -> bool:
        """删除缓存"""
        try:
            return bool(redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """删除匹配模式的所有缓存"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    @staticmethod
    def exists(key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return bool(redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
