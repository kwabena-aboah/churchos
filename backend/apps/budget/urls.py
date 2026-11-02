from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetYearViewSet, BudgetCategoryViewSet, BudgetLineViewSet, BudgetAmendmentViewSet

router = DefaultRouter()
router.register("years", BudgetYearViewSet, basename="budget-year")
router.register("categories", BudgetCategoryViewSet, basename="budget-category")
router.register("lines", BudgetLineViewSet, basename="budget-line")
router.register("amendments", BudgetAmendmentViewSet, basename="budget-amendment")

urlpatterns = [path("", include(router.urls))]
