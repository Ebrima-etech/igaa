from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HotelViewSet, RoomViewSet, RoomAssignmentViewSet, RoomAssignmentBatchViewSet,
    AirportViewSet, FlightViewSet, FlightAssignmentViewSet, FlightBatchViewSet
)

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'room-assignments', RoomAssignmentViewSet, basename='room-assignment')
router.register(r'room-assignment-batches', RoomAssignmentBatchViewSet, basename='room-assignment-batch')
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'flight-assignments', FlightAssignmentViewSet, basename='flight-assignment')
router.register(r'flight-batches', FlightBatchViewSet, basename='flight-batch')

urlpatterns = [
    path('', include(router.urls)),
]
