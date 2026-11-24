"""Django admin: a free UI at http://localhost:8000/admin to look at your data.
Create a login first:  python manage.py createsuperuser
"""

from django.contrib import admin

# TODO Week 1 (optional but useful):
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "source", "created_at"]
    search_fields = ["title", "company"]
    list_filter = ["source"]
