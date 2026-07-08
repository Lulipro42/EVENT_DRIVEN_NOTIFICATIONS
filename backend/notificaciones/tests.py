from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import Cliente
from django.db import connection
from django.core.cache import cache  
# Create your tests here.
User = get_user_model()

class ClienteTests(APITestCase):
    """
    Suite de pruebas unitarias robusta para la creación de clientes.
    Garantiza aislamiento en CI/CD y validación de seguridad perimetral.
    """

    @classmethod
    def setUpTestData(cls):
        """Optimización de rendimiento para CI/CD: Carga datos en memoria una sola vez."""
        cls.url_registro = reverse('registro_usuario')
        
        # 🚨 LÍNEA DE ESPIONAJE: Vamos a ver qué imprime la consola acá
        print(f"\n[DEBUG PORTFOLIO] La URL resuelta por el test es: {cls.url_registro}\n")
        
        cls.datos_validos = {
            
            "email": "dev@portfolio.com",
            "password": "SecurePassword123!"
        }

class ClienteTests(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.url_registro = reverse('registro_usuario')
        cls.datos_validos = {
            "email": "dev@portfolio.com",
            "password": "SecurePassword123!"
        }

    def tearDown(self):
        """
        Garantiza el aislamiento de los tests: Limpia la caché de Throttling 
        después de cada prueba para que un test no bloquee a los demás.
        """
        cache.clear()
        super().tearDown()


    @patch('notificaciones.tasks.enviar_email_tarea.delay')
    def test_registro_exitoso_y_disparo_de_tareas_asincronas(self, mock_celery_task):
        """Verifica que el flujo feliz persista los datos y delegue a Celery de forma segura."""
        # Act
        response = self.client.post(self.url_registro, data=self.datos_validos, format='json')
        
        # Assert: Capa de transporte (API)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)
        
        # Assert: Capa de persistencia (BD)
        cliente_creado = Cliente.objects.filter(email=self.datos_validos["email"]).first()
        self.assertIsNotNone(cliente_creado)
        
        # Assert: Seguridad perimetral (No exponer passwords)
        self.assertNotIn('password', response.data)
        
        # Assert: Desacoplamiento de infraestructura asíncrona
        mock_celery_task.assert_called_once_with(cliente_creado.id)
    
    def test_registro_falla_por_payload_invalido(self):
        """Garantiza que la capa de validación (Serializers) bloquee emails corruptos (400)."""
        payload_corrupto = {"email": "no_es_un_email"}
        response = self.client.post(self.url_registro, data=payload_corrupto, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_limite_de_peticiones_registro_throttling(self):
        """Prueba de estrés: Verifica el bloqueo del middleware ante ráfagas de peticiones (429)."""
        limite_maximo = 5
        
        for i in range(limite_maximo + 1):
            datos_dinamicos = {
                "email": f"dev_{i}@portfolio.com",
                "password": "SecurePassword123!"
            }
            response = self.client.post(self.url_registro, data=datos_dinamicos, format='json')
            
            if i < limite_maximo:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)