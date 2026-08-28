from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardReportViewSet, OperationalMetricViewSet, DashboardSummaryViewSet

router = DefaultRouter()
router.register(r'dashboard-reports', DashboardReportViewSet)
router.register(r'operational-metrics', OperationalMetricViewSet)
router.register(r'dashboard', DashboardSummaryViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
