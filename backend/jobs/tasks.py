"""Week 2: Celery tasks for fetching jobs. Do not import this file before Week 2.

Rules for every task:
- Pass only simple values (ids, strings) into tasks, never model objects.
- A task may run twice (retries, crashes), so make it safe to repeat (idempotent).
"""

from celery import shared_task


@shared_task
def fetch_source(source_name: str) -> dict:
    """Fetch one source and save new jobs. Returns {"source", "found", "new"}.

    1. run = FetchRun.objects.create(source=source_name)
    2. items = sources.SOURCES[source_name]()            (list of dicts, Job-shaped)
    3. Save new ones in ONE query:
           Job.objects.bulk_create([Job(**i) for i in items], ignore_conflicts=True)
       ignore_conflicts skips duplicate urls, but then you don't get ids back.
       To know which are new: first collect existing urls with
           Job.objects.filter(url__in=urls).values_list("url", flat=True)
    4. Update run: status="success", jobs_found, jobs_new, finished_at=timezone.now()
    5. Week 3: if new ids: match_new_jobs.delay(new_ids) and bump_jobs_version()
    On any error: save status="failed", error=str(e)[:1000], then re-raise.

    Retries: change the decorator to
        @shared_task(bind=True, autoretry_for=(requests.RequestException,),
                     retry_backoff=True, max_retries=3)
    """
    raise NotImplementedError("TODO Week 2: fetch_source")


@shared_task
def fetch_all_sources() -> list[str]:
    """Start fetch_source for every name in sources.SOURCES. Celery Beat runs this hourly.

    Hint: celery.group(fetch_source.s(name) for name in SOURCES).apply_async()
    Return the task ids.
    """
    raise NotImplementedError("TODO Week 2: fetch_all_sources")
