"""Week 3: alerts ("tell me when a Python + Redis job appears")."""

from django.db import models  # noqa: F401

# TODO Week 3: uncomment and finish, then makemigrations + migrate
#
# from django.contrib.postgres.fields import ArrayField
#
# class Alert(models.Model):
#     class Channel(models.TextChoices):
#         TELEGRAM = "telegram"
#         EMAIL = "email"
#
#     name = models.CharField(max_length=100)
#     keywords = ArrayField(models.CharField(max_length=50), default=list, blank=True)  # match title
#     skills = ArrayField(models.CharField(max_length=50), default=list, blank=True)    # match job skills
#     channel = models.CharField(max_length=10, choices=Channel.choices)
#     target = models.CharField(max_length=200)   # Telegram chat id or email address
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ["-created_at"]
#
#
# class AlertMatch(models.Model):
#     """A job that matched an alert. The unique pair stops sending the same job twice."""
#     alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="matches")
#     job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE)
#     sent_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=["alert", "job"], name="unique_alert_job"),
#         ]
#         ordering = ["-created_at"]
