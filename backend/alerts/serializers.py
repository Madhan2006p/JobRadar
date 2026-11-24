from rest_framework import serializers


class AlertSerializer(serializers.ModelSerializer):
    """Week 3. Fields: id, name, keywords, skills, channel, target, is_active, created_at.

    TODO Week 3:
        class Meta: model = Alert; fields = [...]; read_only_fields = ["id", "created_at"]
        def validate(self, data):
            keywords and skills cannot BOTH be empty -> raise serializers.ValidationError
        Also lowercase and clean keywords and skills (like JobSerializer.validate_skills).
    """


class AlertMatchSerializer(serializers.ModelSerializer):
    """Week 3. One item of GET /alerts/{id}/matches: {"job": {...Job...}, "sent_at"}.

    TODO Week 3: job = JobSerializer(read_only=True)
                 class Meta: model = AlertMatch; fields = ["job", "sent_at"]
    Interview topic: use select_related("job") in the view, or you get the
    N+1 query problem (1 query for matches + 1 query per job).
    """
