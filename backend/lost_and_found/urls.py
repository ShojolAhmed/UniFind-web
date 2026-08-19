from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from items.api import (
    ItemViewSet,
    ClaimViewSet,
    NotificationViewSet,
    RegisterView,
    MeView,
    MyTokenObtainPairView,
    health,
)


router = DefaultRouter()
router.register('items', ItemViewSet, basename='item')
router.register('claims', ClaimViewSet, basename='claim')
router.register('notifications', NotificationViewSet, basename='notification')


api_urlpatterns = [
    path('health/', health, name='health'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
]


# Serve uploaded media locally only when Cloudinary is not configured.
if settings.DEBUG and not settings.USE_CLOUDINARY:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
