from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, WorkerViewSet, PayrollRunViewSet, PayslipViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("payroll-runs", PayrollRunViewSet, basename="payroll-run")
router.register("payslips", PayslipViewSet, basename="payslip")
router.register("leave-requests", LeaveRequestViewSet, basename="leave-request")
router.register("", WorkerViewSet, basename="worker")

urlpatterns = [path("", include(router.urls))]
