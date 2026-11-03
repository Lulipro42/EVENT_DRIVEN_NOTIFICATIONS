from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import ClienteSerializer
from notificaciones.tasks import enviar_email_tarea

class ClienteCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ClienteSerializer

    def perform_create(self, serializer):
            cliente_creado = serializer.save()
            transaction.on_commit(lambda: enviar_email_tarea.delay(cliente_creado.id))