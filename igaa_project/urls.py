from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/me/', auth_me, name='auth_me'),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('pilgrim.urls')),
    path('api/v1/', include('payment.urls')),
    path('api/v1/', include('banks.urls')),
    path('api/v1/', include('dashboard.urls')),
    path('api/v1/', include('settings_app.urls')),
    path('api/v1/', include('accommodations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Always serve media files (logos, documents, etc)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
