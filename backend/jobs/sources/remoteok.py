"""Week 2: Remote OK public API (free, no key).

Read their API terms first. They ask you to link back to the original job,
which we do through the job url.
"""

API_URL = "https://remoteok.com/api"
SOURCE = "remoteok"
HEADERS = {"User-Agent": "JobRadar learning project"}


def fetch_raw() -> list[dict]:
    """GET API_URL with HEADERS and timeout=10. Return the list of jobs.

    Careful: the FIRST item of the list is a legal notice, not a job. Skip it.
    """
    raise NotImplementedError("TODO Week 2: remoteok.fetch_raw")


def normalize(raw: dict) -> dict:
    """Map: position -> title, company, location, url, tags -> skills,
    date (ISO string) -> posted_at. source = SOURCE.
    """
    raise NotImplementedError("TODO Week 2: remoteok.normalize")


def fetch() -> list[dict]:
    """fetch_raw -> normalize each item -> return the list."""
    raise NotImplementedError("TODO Week 2: remoteok.fetch")
