from __future__ import annotations
import httpx, time

class OrionClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cache = {}
        self.ttl = 30

    def _get_cached(self, key):
        v = self.cache.get(key)
        if v and v["exp"] > time.time():
            return v["val"]
        return None

    def _set_cached(self, key, val):
        self.cache[key] = {"val": val, "exp": time.time()+self.ttl}

    def eval(self, key: str, context: dict) -> bool:
        cached = self._get_cached((key, tuple(sorted(context.items()))))
        if cached is not None:
            return cached
        r = httpx.post(f"{self.base_url}/eval", json={"key": key, "context": context}, timeout=10.0)
        r.raise_for_status()
        val = bool(r.json().get("value", False))
        self._set_cached((key, tuple(sorted(context.items()))), val)
        return val
