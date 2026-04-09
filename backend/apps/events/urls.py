from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventRegistrationViewSet, EventAttendanceViewSet

router = DefaultRouter()
router.register("registrations", EventRegistrationViewSet, basename="event-registration")
router.register("attendance", EventAttendanceViewSet, basename="event-attendance")
router.register("", EventViewSet, basename="event")

urlpatterns = [path("", include(router.urls))]
