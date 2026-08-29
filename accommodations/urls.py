from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, RoomViewSet, RoomAssignmentViewSet, RoomAssignmentBatchViewSet

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'room-assignments', RoomAssignmentViewSet, basename='room-assignment')
router.register(r'room-assignment-batches', RoomAssignmentBatchViewSet, basename='room-assignment-batch')

urlpatterns = [
    path('', include(router.urls)),
]
