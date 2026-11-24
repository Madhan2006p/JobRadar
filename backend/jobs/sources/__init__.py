"""Week 2: every job source, by name. Each value is a function that returns a
list of dicts shaped like the Job model (title, company, location, url, source,
skills, posted_at).

Use only public APIs that allow this, and follow each site's terms.
Do NOT scrape LinkedIn, Naukri or Indeed: their terms forbid it.
"""

from . import arbeitnow, remoteok

SOURCES = {
    "arbeitnow": arbeitnow.fetch,
    "remoteok": remoteok.fetch,
}
