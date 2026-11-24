"""Week 3: Redis cache helpers for GET /jobs (Django cache framework, Redis backend).

Pattern: "cache-aside". Read the cache; on a miss, read the database and
store the result with a timeout (TTL). Know this name for interviews.

Invalidation trick used here: "key versioning". Every cache key contains a
version number. When jobs change, we just increase the version, so all old
keys are never read again and expire by themselves. No need to search Redis
for keys (that would need SCAN, and KEYS * blocks Redis: classic interview point).
"""

from django.core.cache import cache  # noqa: F401  (used once you fill the TODOs)

VERSION_KEY = "jobs:version"


def jobs_version() -> int:
    """Return the current version (cache.get(VERSION_KEY)); if missing, set it to 1."""
    raise NotImplementedError("TODO Week 3: jobs_version")


def bump_jobs_version() -> None:
    """Increase the version by one. Call after any job is added or deleted.

    cache.incr is atomic in Redis (INCR), so two workers can't lose an update.
    If the key does not exist, cache.incr raises ValueError: set it to 1 instead.
    """
    raise NotImplementedError("TODO Week 3: bump_jobs_version")


def cache_key(query_params) -> str:
    """Build a stable key from the request's query params and the version, e.g.
    "jobs:v3:limit=20&offset=0&search=python". Sort the params so their order
    in the URL never matters.
    """
    raise NotImplementedError("TODO Week 3: cache_key")
