from django.urls import path

from . import views

urlpatterns = [
    path("stats/summary", views.summary),
    path("stats/jobs-per-day", views.jobs_per_day),
    path("stats/top-skills", views.top_skills),
    path("stats/top-companies", views.top_companies),
]
