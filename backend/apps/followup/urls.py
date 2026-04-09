from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FollowUpCaseViewSet, FollowUpLogViewSet

router = DefaultRouter()
router.register("logs", FollowUpLogViewSet, basename="followup-log")
router.register("", FollowUpCaseViewSet, basename="followup-case")

urlpatterns = [path("", include(router.urls))]
