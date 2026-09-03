from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardReportViewSet, OperationalMetricViewSet, DashboardSummaryViewSet, HajjYearViewSet,
    NotificationViewSet, UserViewSet, ChatMessageViewSet, ChatGroupViewSet, GroupMessageViewSet
)

router = DefaultRouter()
router.register(r'hajj-years', HajjYearViewSet)
router.register(r'dashboard-reports', DashboardReportViewSet)
router.register(r'operational-metrics', OperationalMetricViewSet)
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'users', UserViewSet, basename='users')
router.register(r'chat-messages', ChatMessageViewSet, basename='chat-messages')
router.register(r'chat-groups', ChatGroupViewSet, basename='chat-groups')
router.register(r'group-messages', GroupMessageViewSet, basename='group-messages')
router.register(r'dashboard/summary', DashboardSummaryViewSet, basename='dashboard-summary')

urlpatterns = [
    path('', include(router.urls)),
]
