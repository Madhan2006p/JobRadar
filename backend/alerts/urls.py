from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("alerts", views.AlertViewSet, basename="alert")

urlpatterns = router.urls
