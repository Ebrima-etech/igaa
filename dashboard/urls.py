from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardReportViewSet, OperationalMetricViewSet, DashboardSummaryViewSet, HajjYearViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'hajj-years', HajjYearViewSet)
router.register(r'dashboard-reports', DashboardReportViewSet)
router.register(r'operational-metrics', OperationalMetricViewSet)
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'dashboard/summary', DashboardSummaryViewSet, basename='dashboard-summary')

urlpatterns = [
    path('', include(router.urls)),
]
