"""
Response Cache

An in-process TTL + LRU cache keyed on the normalized question.
Repeated questions (very common in a tutoring app) return instantly
instead of paying a full generation.
"""

import hashlib
import re
import threading
import time
from collections import OrderedDict
from typing import Any, Optional

from app.config.settings import settings

_WHITESPACE = re.compile(r"\s+")


def make_key(*parts: str) -> str:
    joined = "||".join(_WHITESPACE.sub(" ", p or "").strip().lower() for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


class ResponseCache:
    def __init__(
        self,
        max_entries: Optional[int] = None,
        ttl_seconds: Optional[int] = None,
    ):
        self._store: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()
        self._lock = threading.Lock()
        self._max = max_entries or settings.CACHE_MAX_ENTRIES
        self._ttl = ttl_seconds or settings.CACHE_TTL_SECONDS

    def get(self, key: str) -> Optional[Any]:
        if not settings.ENABLE_RESPONSE_CACHE:
            return None

        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            expires_at, value = entry
            if time.time() > expires_at:
                self._store.pop(key, None)
                return None

            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        if not settings.ENABLE_RESPONSE_CACHE:
            return

        with self._lock:
            self._store[key] = (time.time() + self._ttl, value)
            self._store.move_to_end(key)
            while len(self._store) > self._max:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


response_cache = ResponseCache()
