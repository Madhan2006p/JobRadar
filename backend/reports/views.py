"""Week 4: /stats endpoints. Each view validates query params and calls reports/queries.py."""

from rest_framework.decorators import api_view


@api_view(["GET"])
def summary(request):
    """GET /stats/summary -> 200 {"total_jobs", "jobs_today", "sources", "active_alerts"}"""
    raise NotImplementedError("TODO Week 4: summary view")


@api_view(["GET"])
def jobs_per_day(request):
    """GET /stats/jobs-per-day?days=14 -> 200 [{"day", "jobs"}, ...]

    days must be an integer from 1 to 90, else 400 {"detail": "..."}.
    """
    raise NotImplementedError("TODO Week 4: jobs_per_day view")


@api_view(["GET"])
def top_skills(request):
    """GET /stats/top-skills?limit=10 -> 200 [{"skill", "jobs"}, ...] (limit 1–50)"""
    raise NotImplementedError("TODO Week 4: top_skills view")


@api_view(["GET"])
def top_companies(request):
    """GET /stats/top-companies?limit=10 -> 200 [{"company", "jobs"}, ...] (limit 1–50)"""
    raise NotImplementedError("TODO Week 4: top_companies view")
