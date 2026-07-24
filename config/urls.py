# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

from dashboard.views import home, DashboardView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    # Accounts app
    path('', include('accounts.urls')),    
    # Projects app
    path('projects/', include('projects.urls')),
    # Ticket app
    path('tickets/', include('tickets.urls')),
    # Dashboard app
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # API app
    path('api/', include('api.urls')),
    # DRF/JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Swagger - OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    # Scalar - OpenAPI schema
    path('api-docs/', TemplateView.as_view(
        template_name='api/scalar.html'), name='scalar'),
    # Notification app
    path('notifications/', include('notifications.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

