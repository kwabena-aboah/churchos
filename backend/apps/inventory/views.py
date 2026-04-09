from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import ItemCategory, InventoryItem, ItemMovement
from apps.core.permissions import IsAdminOrReadOnly, IsFinanceOrAbove


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = "__all__"


class ItemMovementSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source="performed_by.get_full_name", read_only=True)

    class Meta:
        model = ItemMovement
        fields = "__all__"
        read_only_fields = ["performed_by"]


class InventoryItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    custodian_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryItem
        fields = [
            "id", "name", "category", "category_name", "condition", "quantity",
            "location", "department", "custodian", "custodian_name",
            "purchase_price", "current_value", "purchase_date", "serial_number", "is_active",
        ]

    def get_custodian_name(self, obj):
        return obj.custodian.get_full_name() if obj.custodian else None


class InventoryItemDetailSerializer(serializers.ModelSerializer):
    movements = ItemMovementSerializer(many=True, read_only=True)
    depreciated_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = InventoryItem
        fields = "__all__"


class ItemCategoryViewSet(viewsets.ModelViewSet):
    queryset = ItemCategory.objects.filter(is_active=True)
    serializer_class = ItemCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.filter(is_active=True).select_related("category", "custodian")
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["name", "serial_number", "barcode", "location"]
    filterset_fields = ["category", "condition", "department", "is_consumable"]

    def get_serializer_class(self):
        return InventoryItemDetailSerializer if self.action == "retrieve" else InventoryItemListSerializer

    @action(detail=True, methods=["post"], url_path="log-movement")
    def log_movement(self, request, pk=None):
        item = self.get_object()
        serializer = ItemMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(item=item, performed_by=request.user)
        if request.data.get("to_location"):
            item.location = request.data["to_location"]
            item.save(update_fields=["location"])
        return Response(serializer.data, status=201)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        from django.db.models import Sum, Count
        data = {
            "total_items": InventoryItem.objects.filter(is_active=True).count(),
            "total_value": InventoryItem.objects.filter(is_active=True).aggregate(v=Sum("current_value"))["v"] or 0,
            "by_condition": list(InventoryItem.objects.filter(is_active=True).values("condition").annotate(count=Count("id"))),
        }
        return Response(data)


class ItemMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ItemMovement.objects.all().select_related("item", "performed_by")
    serializer_class = ItemMovementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["item", "movement_type"]


router = DefaultRouter()
router.register("categories", ItemCategoryViewSet, basename="item-category")
router.register("movements", ItemMovementViewSet, basename="item-movement")
router.register("", InventoryItemViewSet, basename="inventory-item")

urlpatterns = [path("", include(router.urls))]
