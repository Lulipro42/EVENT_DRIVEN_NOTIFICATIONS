from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Aquí incluyes todas las rutas de tu app 'notificaciones'
    path('', include('notificaciones.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='registro_usuario'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
