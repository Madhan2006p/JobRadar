"""Project-level views that don't belong to one app."""

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(request):
    """GET /health -> 200 {"status": "ok"}

    Week 2 idea: also check the database (connection.ensure_connection())
    and Redis (ping), and return 503 if either is down.
    """
    return Response({"status": "ok"})
