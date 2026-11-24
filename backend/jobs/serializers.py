"""Serializers turn model objects into JSON and check incoming JSON.
They must match docs/api-contract.md.
"""

from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """Used by every /jobs endpoint. (Week 1, WEEK1.md Step 7)

    TODO Week 1:
        class Meta:
            model = Job
            fields = ["id", "title", "company", "location", "url", "source",
                      "skills", "posted_at", "created_at"]
            read_only_fields = ["id", "created_at"]

    TODO Week 1: def validate_skills(self, value):
        strip spaces, lowercase, drop empty items, remove duplicates; return the list.

    Note: because url is unique=True on the model, DRF adds a UniqueValidator for you,
    so a duplicate url returns 400 {"url": ["job with this url already exists."]}.
    Interview topic: two requests with the same url at the SAME moment can both pass
    this check. Who stops the second one? (The database UNIQUE constraint.)
    """

    skills = serializers.ListField(
        child=serializers.CharField(max_length=50, allow_blank=True),
        required=False,
    )
    
    class Meta:
        model = Job
        fields = ["id" , "title" , "company" , "location" , "url" , "source" , "skills" , "posted_at" , "created_at"]
        read_only_fields = ["id" , "created_at"]

    def validate_skills(self, value):

        # Stipe by space
        cleaned =  [skill.strip().lower() for skill in value]

        # drop empty items 
        cleaned = [skill for skill in cleaned if skill]

        # Remove duplicates 
        cleaned = list(dict.fromkeys(cleaned))

        # Return list
        return cleaned



# TODO Week 2
# class SourceSerializer(serializers.Serializer):
#     """One item of GET /sources (not a model, so a plain Serializer)."""
#     name = serializers.CharField()
#     jobs = serializers.IntegerField()
#     last_run_at = serializers.DateTimeField(allow_null=True)
#     last_status = serializers.CharField(allow_null=True)
