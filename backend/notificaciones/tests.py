from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.db import connection
# Create your tests here.
User = get_user_model()

class ClienteTests(APITestCase):
    """
    Suite de pruebas unitarias ajustada a tu lógica de persistencia (email como username).
    """
    
    @classmethod
    def setUpTestData(cls):
        cls.url_registro = reverse('crear_view') # Ajustado al nombre en tus urls.py
        cls.datos_validos = {
            "email": "dev@portfolio.com",
            "password": "SecurePassword123!"
        }

    def test_disparar_notificacion_endpoint_is_available(self):
        response = self.client.get(reverse('disparar_notifiacion'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.json())

    @patch('notificaciones.tasks.enviar_email_tarea.delay')
    def test_registro_exitoso_y_disparo_de_tareas_asincronas(self, mock_celery_task):
        # Act
        response = self.client.post(self.url_registro, data=self.datos_validos, format='json')
        
        self.assertIn('access', response.data)
        self.assertIn('refresh',response.data)
        
        self.assertIsInstance(response.data['access'], str)
                
        # Assert: Capa de transporte (API) - Debe ser 201 Created, no 401
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert: Capa de persistencia (BD)
        # Buscamos por email porque tu serializer usa email como username
        usuario_creado = User.objects.filter(email=self.datos_validos["email"]).first()
        self.assertIsNotNone(usuario_creado)
        
        # Assert: Seguridad - Validamos que no exponga la contraseña
        self.assertNotIn('password', response.data)
        
        # Assert: Celery
        mock_celery_task.assert_called_once_with(1)
        
    def test_registro_falla_por_payload_invalido(self):
        """
        Garantiza que la capa de validación bloquee payloads corruptos.
        """
        payload_corrupto = {"email": "no_es_un_email"}
        response = self.client.post(self.url_registro, data=payload_corrupto, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def limite(self):
        # 1. ARRANGE: Definir cuántas peticiones máximas permitís (ej: 5)
        limite_maximo = 5
        # 2. ACT & ASSERT: El bucle que va a estresar el endpoint    
        for i in range(limite_maximo + 1 ):
            # Crear datos únicos usando la variable 'i' para evitar errores de duplicados    
            datos_dinamicos = {
                "user":f"ingeniero_{i}",
                "email":f"dev_{i}@portfolio.com",
                "password":"SecurePassword123!"
            }
           # Ejecutar la acción
            response = self.client.post(self.url_registro, data=datos_dinamicos, format='json')
            
            # Evaluar el comportamiento según la iteración
            if i < limite_maximo:
                # Las primeras 5 veces tiene que dejarte crear el usuario
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                
            else:
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
