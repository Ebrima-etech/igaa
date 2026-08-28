from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PilgrimViewSet, PilgrimDocumentViewSet

router = DefaultRouter()
router.register(r'pilgrims', PilgrimViewSet, basename='pilgrim')
router.register(r'pilgrim-documents', PilgrimDocumentViewSet, basename='pilgrim-document')

urlpatterns = [
    path('', include(router.urls)),
]
