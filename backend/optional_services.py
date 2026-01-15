from __future__ import annotations

import json
from typing import Any

from .app_config import settings

try:
    import redis  # type: ignore
except Exception:
    redis = None  # type: ignore

try:
    from elasticsearch import Elasticsearch  # type: ignore
except Exception:
    Elasticsearch = None  # type: ignore


def get_redis_client():
    if not settings.REDIS_URL or not redis:
        return None
    try:
        return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        return None


def cache_get(client, key: str) -> Any | None:
    if not client:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(client, key: str, value: Any, ttl: int = 300) -> None:
    if not client:
        return
    try:
        client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception:
        return


def get_es_client():
    if not settings.ELASTICSEARCH_URL or not Elasticsearch:
        return None
    try:
        return Elasticsearch(settings.ELASTICSEARCH_URL)
    except Exception:
        return None