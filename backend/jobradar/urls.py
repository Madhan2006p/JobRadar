"""All URLs. No trailing slashes, to match docs/api-contract.md (/jobs, not /jobs/)."""

from django.contrib import admin
from django.urls import include, path

from .views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health),
    path("", include("jobs.urls")),       # Week 1 (+ /fetch, /tasks, /sources in Week 2)
    # path("", include("alerts.urls")),   # Week 3: uncomment
    # path("", include("reports.urls")),  # Week 4: uncomment
]
