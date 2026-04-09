from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChurchSettingsView,
    ChurchSettingsPublicView,
    ServiceTypeViewSet,
    ZoneViewSet,
    CellGroupViewSet,
)

router = DefaultRouter()
router.register("service-types", ServiceTypeViewSet, basename="service-type")
router.register("zones", ZoneViewSet, basename="zone")
router.register("cell-groups", CellGroupViewSet, basename="cell-group")

urlpatterns = [
    path("settings/", ChurchSettingsView.as_view(), name="church-settings"),
    path("settings/public/", ChurchSettingsPublicView.as_view(), name="church-settings-public"),
    path("", include(router.urls)),
]
