from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from .serializers import ClienteSerializer
from .models import Cliente
from rest_framework import generics,status
from rest_framework.exceptions import ValidationError
from .tasks import enviar_email_tarea
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .services import  procesar_registro_exitoso
# Create your views here.

class ClienteCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClienteSerializer  # <--- YA CORREGIDO (sin la 'a' extra)

    def perform_create(self, serializer):
        # 1. El serializer (que ya configuraste) hace el trabajo de persistencia
        # y nos devuelve la instancia del cliente recién creado.
        cliente_creado = serializer.save()
        
        # 2. Delegamos la lógica secundaria (notificaciones, tareas) al servicio.
        # La vista no se ensucia con lógica de Celery o correos.
        procesar_registro_exitoso(cliente_creado)
        
    def create(self, request, *args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            "mensjae":"!Usuario registrado con exito",
            "id": serializer.instance.id
        }, status=status.HTTP_201_CREATED)