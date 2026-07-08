import random
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
# Create your models here.

class Cliente(models.Model):

    user = models.OneToOneField(User, on_delete=models.SET_NULL,null=True, related_name='cliente') # Bueno aca basandome en demas codigos puse el user ya que luego voy a crear una variable user/cliente, luego puse ontefield debido a la seguridad, para que nadie mas pueda acceder a su usario, leugo el set null para tambien tema de seguiradad 
    
    email = models.EmailField(unique=True, null=True, blank=True)
        # Seguridad: Nadie más puede usar este correo
        # Permite que quede vacío en la base de datos
        # Permite que quede vacío en los formularios
        

    def __str__(self) -> str:
        return self.email if self.email else "Sin email"