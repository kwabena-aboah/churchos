from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, FinanceCategoryViewSet, BankAccountViewSet, CauseViewSet, PledgeViewSet

router = DefaultRouter()
router.register("transactions", TransactionViewSet, basename="transaction")
router.register("categories", FinanceCategoryViewSet, basename="finance-category")
router.register("bank-accounts", BankAccountViewSet, basename="bank-account")
router.register("causes", CauseViewSet, basename="cause")
router.register("pledges", PledgeViewSet, basename="pledge")

urlpatterns = [path("", include(router.urls))]
