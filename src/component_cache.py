# Copyright (c) Meta Platforms, Inc. and affiliates
"""
Cache for already-processed component source code.

After DocAgent generates a docstring for a component and writes it to the file,
the updated source (code + docstring) is stored here keyed by component_id
(e.g. "models.product.Item"). Subsequent components that depend on the same
component retrieve its source from cache instead of re-reading the file via AST.
"""

from typing import Dict, Optional


class ComponentCache:
    """In-memory store mapping component_id → updated source code with docstring."""

    def __init__(self) -> None:
        self._cache: Dict[str, str] = {}
        self._hit_count: int = 0
        self._miss_count: int = 0

    def register(self, component_id: str, source: str) -> None:
        """Store the updated source of a completed component.

        Args:
            component_id: Dot-separated dependency path, e.g. "models.product.Item"
            source: Source code of the component (with generated docstring included)
        """
        self._cache[component_id] = source

    def get(self, component_id: str) -> Optional[str]:
        """Retrieve cached source, or None if not cached.

        Args:
            component_id: Dot-separated dependency path

        Returns:
            Cached source string, or None on cache miss
        """
        result = self._cache.get(component_id)
        if result is not None:
            self._hit_count += 1
        else:
            self._miss_count += 1
        return result

    def __contains__(self, component_id: str) -> bool:
        return component_id in self._cache

    # ------------------------------------------------------------------
    # Stats (for analytics / debugging)
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def hit_count(self) -> int:
        return self._hit_count

    @property
    def miss_count(self) -> int:
        return self._miss_count

    def stats(self) -> Dict[str, int]:
        total = self._hit_count + self._miss_count
        return {
            "cached_components": self.size,
            "cache_hits": self._hit_count,
            "cache_misses": self._miss_count,
            "hit_rate_pct": round(100 * self._hit_count / total, 1) if total else 0,
        }
