import datetime
from django.conf import settings
from django.core.cache import cache

def _today_str() -> str:
    """
    Return today’s date in ISO format (YYYY-MM-DD).
    Example: "2025-06-04"
    """
    return datetime.date.today().isoformat()

def _viewed_cache_key(visitor_identifier:str, book_id: int, date_str: str) -> str:
    """
    Build a cache key for "visitor {visitor_identifier} has viewed {book_id} on {date_str}".
    We will set this key with a TTL of 24 hours so that tomorrow it auto-expires.
    """
    return f'{visitor_identifier}:{book_id}:{date_str}'

def has_viewed_today(visitor_identifier:str, book_id: int) -> bool:
    """
    Return True if the cache says this visitor already viewed this book today.
    """
    key = _viewed_cache_key(visitor_identifier, book_id, _today_str())
    return cache.get(key) is not None

def mark_viewed_today(visitor_identifier:str, book_id: int) -> None:
    """
    Mark in the cache that `visitor_identifier` has viewed `book_id` today.
    We set a TTL of exactly 24 hours (BOOK_VIEW_TTL).
    """
    key = _viewed_cache_key(visitor_identifier, book_id, _today_str())
    cache.set(key, True, timeout=settings.BOOK_VIEW_TTL)