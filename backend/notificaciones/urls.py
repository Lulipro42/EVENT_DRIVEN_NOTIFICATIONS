from django.urls import path
from .views import ClienteCreateView


urlpatterns = [
    
    path('api/crear-view/', ClienteCreateView.as_view(), name="crear_view"),
]