import random
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class EstadoEmail(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    EN_PROCESO = 'EN_PROCESO', 'En Proceso'
    ENVIADO = 'ENVIADO', 'Enviado'
    FALLIDO = 'FALLIDO', 'Fallido'

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='cliente')
    email = models.EmailField(unique=True, null=True, blank=True)
    estado_email_bienvenida = models.CharField(
        max_length=20,
        choices=EstadoEmail.choices,
        default=EstadoEmail.PENDIENTE
    )
    intentado_en = models.DateTimeField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.email if self.email else "Sin email"