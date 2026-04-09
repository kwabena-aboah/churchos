from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core.reports import (
    FinanceReportView, MembersReportView, AttendanceReportView,
    PayrollReportView, TitheReportView, InventoryReportView, AuditReportExportView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/core/", include("apps.core.urls")),
    path("api/v1/members/", include("apps.members.urls")),
    path("api/v1/finance/", include("apps.finance.urls")),
    path("api/v1/communication/", include("apps.communication.urls")),
    path("api/v1/events/", include("apps.events.urls")),
    path("api/v1/followup/", include("apps.followup.urls")),
    path("api/v1/workers/", include("apps.workers.urls")),
    path("api/v1/sermons/", include("apps.sermons.urls")),
    path("api/v1/budget/", include("apps.budget.urls")),
    path("api/v1/inventory/", include("apps.inventory.urls")),
    path("api/v1/procurement/", include("apps.procurement.urls")),
    path("api/v1/prayer/", include("apps.prayer.urls")),
    path("api/v1/discipleship/", include("apps.discipleship.urls")),
    path("api/v1/facility/", include("apps.facility.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/v1/cellgroups/", include("apps.cellgroups.urls")),
    # ── Reports ─────────────────────────────────────────────────────────────────
    path("api/v1/reports/finance/", FinanceReportView.as_view(), name="report-finance"),
    path("api/v1/reports/members/", MembersReportView.as_view(), name="report-members"),
    path("api/v1/reports/attendance/", AttendanceReportView.as_view(), name="report-attendance"),
    path("api/v1/reports/payroll/", PayrollReportView.as_view(), name="report-payroll"),
    path("api/v1/reports/tithes/", TitheReportView.as_view(), name="report-tithes"),
    path("api/v1/reports/inventory/", InventoryReportView.as_view(), name="report-inventory"),
    path("api/v1/reports/audit/", AuditReportExportView.as_view(), name="report-audit"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

