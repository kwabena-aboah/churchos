"""
Cell Groups views — leverages the CellGroup and Zone models from apps.core.
This app provides additional cell-group-specific analytics endpoints.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core.models import CellGroup, Zone
from apps.core.serializers import CellGroupSerializer, ZoneSerializer
from apps.core.permissions import IsAdminOrReadOnly


class CellGroupAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Extended cell group viewset with member stats and attendance analytics.
    The base CRUD is handled by apps.core.views.CellGroupViewSet.
    """
    queryset = CellGroup.objects.filter(is_active=True).select_related("zone")
    serializer_class = CellGroupSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        group = self.get_object()
        from apps.members.models import Member, MemberStatus
        members = Member.objects.filter(cell_group=group, is_active=True)
        active = members.filter(membership_status=MemberStatus.ACTIVE).count()
        visitors = members.filter(membership_status=MemberStatus.VISITOR).count()
        return Response({
            "cell_group": group.name,
            "zone": group.zone.name if group.zone else None,
            "total_members": members.count(),
            "active": active,
            "visitors": visitors,
            "members": [
                {
                    "id": str(m.id),
                    "name": m.get_full_name(),
                    "phone": m.phone_primary,
                    "status": m.membership_status,
                }
                for m in members[:50]
            ]
        })

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        from apps.members.models import Member
        from django.db.models import Count
        groups = (
            CellGroup.objects
            .filter(is_active=True)
            .annotate(member_count=Count("members"))
            .select_related("zone")
            .order_by("zone__name", "name")
        )
        return Response([
            {
                "id": str(g.id),
                "name": g.name,
                "zone": g.zone.name if g.zone else None,
                "member_count": g.member_count,
            }
            for g in groups
        ])


router = DefaultRouter()
router.register("", CellGroupAnalyticsViewSet, basename="cellgroup-analytics")

urlpatterns = [path("", include(router.urls))]
