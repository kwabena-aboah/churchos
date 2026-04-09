from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageTemplateViewSet, MessageLogViewSet, BroadcastViewSet

router = DefaultRouter()
router.register("templates", MessageTemplateViewSet, basename="message-template")
router.register("logs", MessageLogViewSet, basename="message-log")
router.register("broadcasts", BroadcastViewSet, basename="broadcast")

urlpatterns = [path("", include(router.urls))]
