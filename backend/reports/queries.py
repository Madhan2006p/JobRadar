"""Week 4: reporting queries in RAW SQL on purpose.

The Django ORM is great for everyday code, but data engineer interviews ask
you to write SQL by hand. Write these as SQL, run them with:

    from django.db import connection
    with connection.cursor() as cur:
        cur.execute(sql, [param1, param2])     # always parameters, never f-strings
        rows = cur.fetchall()

Table names: jobs_job, alerts_alert (Django names them "<app>_<model>").
Tip: try every query first in psql:  docker compose exec db psql -U jobradar
"""


def summary() -> dict:
    """{"total_jobs", "jobs_today", "sources", "active_alerts"}

    Hint: several counts in one query with FILTER:
      COUNT(*) FILTER (WHERE created_at >= date_trunc('day', now()))
    """
    raise NotImplementedError("TODO Week 4: summary")


def jobs_per_day(days: int) -> list[dict]:
    """[{"day": "2026-11-01", "jobs": 12}, ...] for the last `days` days, oldest first,
    INCLUDING days with 0 jobs.

    Hint: generate_series(current_date - (%s - 1), current_date, interval '1 day')
          LEFT JOIN jobs_job ON created_at::date = day ... GROUP BY day
    """
    raise NotImplementedError("TODO Week 4: jobs_per_day")


def top_skills(limit: int) -> list[dict]:
    """[{"skill": "python", "jobs": 40}, ...] most common first.

    Hint: SELECT unnest(skills) AS skill, COUNT(*) FROM jobs_job GROUP BY skill ...
    """
    raise NotImplementedError("TODO Week 4: top_skills")


def top_companies(limit: int) -> list[dict]:
    """[{"company": "Acme", "jobs": 7}, ...] (GROUP BY company)."""
    raise NotImplementedError("TODO Week 4: top_companies")
