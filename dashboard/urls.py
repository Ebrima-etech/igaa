from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardReportViewSet, OperationalMetricViewSet, DashboardSummaryViewSet, HajjYearViewSet

router = DefaultRouter()
router.register(r'hajj-years', HajjYearViewSet)
router.register(r'dashboard-reports', DashboardReportViewSet)
router.register(r'operational-metrics', OperationalMetricViewSet)
router.register(r'dashboard', DashboardSummaryViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
