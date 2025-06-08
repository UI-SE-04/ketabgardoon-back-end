import datetime
from django.conf import settings
from django.core.cache import cache

def _today_str() -> str:
    """
    Return today’s date in ISO format (YYYY-MM-DD).
    Example: "2025-06-04"
    """
    return datetime.date.today().isoformat()

def _viewed_cache_key(visitor_identifier: str,
                      object_type: str,
                      object_id: int,
                      date_str: str) -> str:
    """
    Build a cache key for "visitor {visitor_identifier} has viewed
    {object_type} {object_id} on {date_str}".
    E.g. "session:XYZ:author:42:2025-06-08"
    """
    return f'{visitor_identifier}:{object_type}:{object_id}:{date_str}'

def has_viewed_today(visitor_identifier: str,
                     object_type: str,
                     object_id: int) -> bool:
    """
    Return True if this visitor has viewed this (type, id) today.
    """
    key = _viewed_cache_key(visitor_identifier,
                            object_type,
                            object_id,
                            _today_str())
    return cache.get(key) is not None

def mark_viewed_today(visitor_identifier: str,
                      object_type: str,
                      object_id: int,
                      ttl: int = None) -> None:
    """
    Mark in the cache that `visitor_identifier` has viewed (type, id) today.
    If `ttl` is not provided, it falls back to settings.DEFAULT_VIEW_TTL.
    """
    key = _viewed_cache_key(visitor_identifier,
                            object_type,
                            object_id,
                            _today_str())
    if ttl is None:
        ttl = settings.DEFAULT_VIEW_TTL
    cache.set(key, True,  timeout=ttl)