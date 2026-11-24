from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

# trailing_slash=False -> /jobs and /jobs/5 (matches the API contract)
router = SimpleRouter(trailing_slash=False)
router.register("jobs", views.JobViewSet, basename="job")

urlpatterns = [
    *router.urls,
    # TODO Week 2: uncomment
    # path("fetch", views.start_fetch),
    # path("tasks/<str:task_id>", views.task_status),
    # path("sources", views.list_sources),
]
