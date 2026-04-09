from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import DiscipleshipTrack, DiscipleshipClass, DiscipleshipEnrollment
from apps.core.permissions import IsAdminOrReadOnly


class DiscipleshipTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscipleshipTrack
        fields = "__all__"


class DiscipleshipClassSerializer(serializers.ModelSerializer):
    track_name = serializers.CharField(source="track.name", read_only=True)
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = DiscipleshipClass
        fields = "__all__"

    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(status__in=["enrolled", "active"]).count()


class DiscipleshipEnrollmentSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.get_full_name", read_only=True)
    class_name = serializers.CharField(source="discipleship_class.__str__", read_only=True)

    class Meta:
        model = DiscipleshipEnrollment
        fields = "__all__"


class DiscipleshipTrackViewSet(viewsets.ModelViewSet):
    queryset = DiscipleshipTrack.objects.filter(is_active=True)
    serializer_class = DiscipleshipTrackSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class DiscipleshipClassViewSet(viewsets.ModelViewSet):
    queryset = DiscipleshipClass.objects.filter(is_active=True).select_related("track", "facilitator")
    serializer_class = DiscipleshipClassSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ["track"]


class DiscipleshipEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = DiscipleshipEnrollment.objects.all().select_related("member", "discipleship_class")
    serializer_class = DiscipleshipEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["discipleship_class", "member", "status"]


router = DefaultRouter()
router.register("tracks", DiscipleshipTrackViewSet, basename="discipleship-track")
router.register("classes", DiscipleshipClassViewSet, basename="discipleship-class")
router.register("enrollments", DiscipleshipEnrollmentViewSet, basename="discipleship-enrollment")

urlpatterns = [path("", include(router.urls))]
