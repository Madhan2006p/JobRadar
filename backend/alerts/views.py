from rest_framework import mixins, viewsets


class AlertViewSet(
    mixins.ListModelMixin,      # GET    /alerts
    mixins.CreateModelMixin,    # POST   /alerts
    mixins.DestroyModelMixin,   # DELETE /alerts/{id}
    viewsets.GenericViewSet,
):
    """Week 3: all /alerts endpoints.

    TODO Week 3:
        queryset = Alert.objects.all()
        serializer_class = AlertSerializer
        pagination_class = None          (alerts are few, return a plain list)

    TODO Week 3: extra endpoint GET /alerts/{id}/matches
        @action(detail=True, methods=["get"])
        def matches(self, request, pk=None):
            alert = self.get_object()          (404 for you if it does not exist)
            qs = alert.matches.select_related("job")[:20]
            return Response(AlertMatchSerializer(qs, many=True).data)
    """
