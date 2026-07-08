from django.urls import path
from .views import ClienteCreateView


urlpatterns = [
    
    path('api/clientes/regiistro/', ClienteCreateView.as_view(), name="registro_usuario"),
]