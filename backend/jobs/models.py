"""Database tables for the jobs app. After every change here, run:
    python manage.py makemigrations
    python manage.py migrate
And look at the real SQL Django wrote:
    python manage.py sqlmigrate jobs 0001
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField

class Job(models.Model):
    """One job post. (Week 1, WEEK1.md Step 4)

    TODO Week 1: add these fields
        title       CharField(max_length=300)
        company     CharField(max_length=200)
        location    CharField(max_length=200, blank=True, default="")
        url         URLField(max_length=500, unique=True)     <- stops duplicates
        source      CharField(max_length=50, default="manual")
        skills      ArrayField(CharField(max_length=50), default=list, blank=True)
                    (from django.contrib.postgres.fields import ArrayField)
        posted_at   DateTimeField(null=True, blank=True)
        created_at  DateTimeField(auto_now_add=True)

    TODO Week 1: class Meta with
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]
    TODO Week 3: add GinIndex(fields=["skills"]) to indexes
        (from django.contrib.postgres.indexes import GinIndex)

    TODO Week 1: def __str__(self): return f"{self.title} at {self.company}"
    """

    title = models.CharField(max_length=300)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, default="")
    url = models.URLField(max_length=500, unique=True)
    source = models.CharField(max_length=50, default="manual")
    skills = ArrayField(models.CharField(max_length=50), default=list, blank=True)  
    posted_at = models.DateTimeField(null=True , blank = True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"{self.title} at {self.company}"


# TODO Week 2: uncomment and finish, then makemigrations + migrate
# class FetchRun(models.Model):
#     """One row per Celery fetch: a log for debugging and for GET /sources."""
#
#     class Status(models.TextChoices):
#         RUNNING = "running"
#         SUCCESS = "success"
#         FAILED = "failed"
#
#     source = models.CharField(max_length=50)
#     status = models.CharField(max_length=10, choices=Status.choices, default=Status.RUNNING)
#     jobs_found = models.IntegerField(default=0)
#     jobs_new = models.IntegerField(default=0)
#     error = models.TextField(blank=True, default="")
#     started_at = models.DateTimeField(auto_now_add=True)
#     finished_at = models.DateTimeField(null=True, blank=True)
#
#     class Meta:
#         indexes = [models.Index(fields=["source", "-started_at"])]
