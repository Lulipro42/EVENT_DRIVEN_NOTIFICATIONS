from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import ClienteSerializer
from .services import procesar_registro_exitoso

class ClienteCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ClienteSerializer

    def perform_create(self, serializer):
        """
        Hook de creación: Guarda en BD (con transaction.atomic en el serializer)
        y delega el efecto secundario seguro (Celery) a nuestro servicio.
        """
        cliente_creado = serializer.save()
        
        # Conectamos con tu función de services.py para disparar la tarea asíncrona
        procesar_registro_exitoso(cliente_creado)
