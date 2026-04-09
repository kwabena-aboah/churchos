from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from django.utils import timezone
from rest_framework.routers import DefaultRouter
from .models import Vendor, PurchaseRequest, PurchaseRequestItem, PurchaseOrder
from apps.core.permissions import IsFinanceOrAbove, IsAdminOrReadOnly


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class PurchaseRequestItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseRequestItem
        fields = "__all__"


class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseRequestItemSerializer(many=True, read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = "__all__"
        read_only_fields = ["reference", "requested_by", "approved_by", "approved_at"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = ["reference", "created_by"]


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.filter(is_active=True)
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["name", "contact_person", "category"]


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.filter(is_active=True).select_related("requested_by", "approved_by")
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "department"]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user, status="pending")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        req = self.get_object()
        req.status = "approved"
        req.approved_by = request.user
        req.approved_at = timezone.now()
        req.save()
        return Response({"status": "approved"})

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        req = self.get_object()
        req.status = "rejected"
        req.rejection_reason = request.data.get("reason", "")
        req.approved_by = request.user
        req.save()
        return Response({"status": "rejected"})


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.filter(is_active=True).select_related("vendor", "created_by")
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, IsFinanceOrAbove]
    filterset_fields = ["status", "vendor"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-received")
    def mark_received(self, request, pk=None):
        order = self.get_object()
        order.status = "received"
        order.actual_delivery = timezone.now().date()
        order.save()
        return Response({"status": "received"})


router = DefaultRouter()
router.register("vendors", VendorViewSet, basename="vendor")
router.register("requests", PurchaseRequestViewSet, basename="purchase-request")
router.register("orders", PurchaseOrderViewSet, basename="purchase-order")

urlpatterns = [path("", include(router.urls))]
