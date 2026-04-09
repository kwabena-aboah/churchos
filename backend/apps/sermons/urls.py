from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpeakerViewSet, SermonSeriesViewSet, SermonViewSet

router = DefaultRouter()
router.register("speakers", SpeakerViewSet, basename="speaker")
router.register("series", SermonSeriesViewSet, basename="sermon-series")
router.register("", SermonViewSet, basename="sermon")

urlpatterns = [path("", include(router.urls))]
