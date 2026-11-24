"""Views for /jobs (Week 1) and /fetch, /tasks, /sources (Week 2)."""

from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view
from .models import Job
from .serializers import JobSerializer


class JobViewSet(
    mixins.ListModelMixin,      # GET    /jobs
    mixins.RetrieveModelMixin,  # GET    /jobs/{id}
    mixins.CreateModelMixin,    # POST   /jobs
    mixins.DestroyModelMixin,   # DELETE /jobs/{id}
    viewsets.GenericViewSet,
):
    """All /jobs endpoints. No PUT/PATCH on purpose: jobs are read-only after saving.

    TODO Week 1 (WEEK1.md Step 8): set these class attributes
        queryset = Job.objects.all()                 (ordering comes from Meta)
        serializer_class = JobSerializer
        search_fields = ["title", "company"]          -> ?search=python
        ordering_fields = ["created_at", "posted_at"] -> ?ordering=-posted_at

    That is all Week 1 needs: the mixins already give you
    200 / 201 / 204 / 400 / 404 with the right bodies. Read the mixin source
    once (Ctrl+click ListModelMixin) to see what DRF does for you.

    TODO Week 3: override list() for the Redis cache (see jobs/cache.py):
        key = cache_key(request.query_params)
        cached = cache.get(key) -> return Response(cached)
        otherwise response = super().list(...); cache.set(key, response.data, JOBS_CACHE_SECONDS)
    TODO Week 3: in perform_create() and perform_destroy(), call bump_jobs_version()
        so old cached pages are never shown again, and queue match_new_jobs for new jobs.
    """

    queryset = Job.objects.all()
    serializer_class = JobSerializer
    search_fields = ["title" , "company"]
    ordering_fields = ["created_at" , "posted_at"]


# ---------------- Week 2 ----------------

@api_view(["POST"])
def start_fetch(request):
    """POST /fetch?source=all|arbeitnow|remoteok -> 202 {"task_id": "...", "source": "..."}

    - 400 {"detail": "Unknown source"} if not "all" and not in sources.SOURCES
    - "all" -> fetch_all_sources.delay(); one name -> fetch_source.delay(name)
    - Return right away with status=202. Never wait for the task here.
    Interview topic: why 202 Accepted and not 200 OK?
    """
    raise NotImplementedError("TODO Week 2: start_fetch")


@api_view(["GET"])
def task_status(request, task_id):
    """GET /tasks/{task_id} -> 200 {"task_id", "state", "result"}

    from celery.result import AsyncResult; r = AsyncResult(task_id)
    state is PENDING / STARTED / RETRY / SUCCESS / FAILURE.
    result only when state == "SUCCESS" (else null). Never send the raw error text
    of a FAILURE to the client: it can leak internal details.
    """
    raise NotImplementedError("TODO Week 2: task_status")


@api_view(["GET"])
def list_sources(request):
    """GET /sources -> 200 [{"name", "jobs", "last_run_at", "last_status"}, ...]

    - jobs per source: Job.objects.values("source").annotate(n=Count("id"))
    - latest run per source: FetchRun.objects.order_by("source", "-started_at")
                             .distinct("source")   (PostgreSQL-only DISTINCT ON)
    - include every name in sources.SOURCES, even with 0 jobs and no runs
    """
    raise NotImplementedError("TODO Week 2: list_sources")
