"""Week 3: match new jobs to alerts and send messages. Don't import before Week 2."""

from celery import shared_task


@shared_task
def match_new_jobs(job_ids: list[int]) -> int:
    """For each new job, find matching active alerts and queue send_alert.

    A job matches an alert when:
      - any alert keyword is inside the job title (case-insensitive), OR
      - alert skills and job skills overlap: Alert.objects.filter(skills__overlap=job.skills)
    For each match: AlertMatch.objects.get_or_create(alert=..., job=...).
    Only when it was CREATED (not already there), queue send_alert.delay(alert.id, job.id).
    That makes this task safe to run twice (idempotent).
    Return how many messages were queued.
    """
    raise NotImplementedError("TODO Week 3: match_new_jobs")


@shared_task
def send_alert(alert_id: int, job_id: int) -> bool:
    """Send one message (notify.send_telegram or notify.send_email), then set sent_at.

    Add retries: @shared_task(bind=True, max_retries=5, retry_backoff=True),
    because Telegram and email servers sometimes fail.
    If sent_at is already set, do nothing (it was sent by an earlier try).
    """
    raise NotImplementedError("TODO Week 3: send_alert")
