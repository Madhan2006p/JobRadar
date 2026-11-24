"""Week 2: Arbeitnow public job board API (free, no key).

Open the URL in your browser first and study the JSON before coding.
"""

API_URL = "https://www.arbeitnow.com/api/job-board-api"
SOURCE = "arbeitnow"


def fetch_raw(page: int = 1) -> list[dict]:
    """GET API_URL?page=N and return the list under "data".

    Use requests.get(..., timeout=10) and resp.raise_for_status().
    Never call an API without a timeout: a stuck request blocks the worker forever.
    """
    raise NotImplementedError("TODO Week 2: arbeitnow.fetch_raw")


def normalize(raw: dict) -> dict:
    """Turn one Arbeitnow item into a Job-shaped dict.

    Map: title, company_name -> company, location, url, tags -> skills,
    created_at (unix seconds) -> posted_at (aware datetime in UTC). source = SOURCE.
    skills = extract_skills(title + tags + description): tags also contain
    non-skills like "Remote", so don't copy them directly.
    """
    raise NotImplementedError("TODO Week 2: arbeitnow.normalize")


def fetch() -> list[dict]:
    """fetch_raw(page=1) -> normalize each item -> return the list.
    Later: read more pages, with a fixed maximum (for example 3).
    """
    raise NotImplementedError("TODO Week 2: arbeitnow.fetch")
