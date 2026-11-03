from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase  
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.core.cache import cache  
from notificaciones.models import Cliente, EstadoEmail
from notificaciones.tasks import enviar_email_tarea
from django.db import connection

User = get_user_model()


class ClienteTests(TransactionTestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url_registro = reverse('registro_usuario')
        self.datos_validos = {
            "email": "dev@portfolio.com",
            "password": "SecurePassword123!"
        }

    def tearDown(self):
        cache.clear()
        super().tearDown()

    @patch('notificaciones.views.enviar_email_tarea.delay')
    def test_registro_exitoso_y_disparo_de_tareas_asincronas(self, mock_celery_task):
        """Verifica que el flujo feliz persista los datos y delegue a Celery tras el commit."""
        response = self.client.post(self.url_registro, data=self.datos_validos, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        cliente_creado = Cliente.objects.filter(email=self.datos_validos["email"]).first()
        self.assertIsNotNone(cliente_creado)
        
        mock_celery_task.assert_called_once_with(cliente_creado.id)
    
    def test_registro_falla_por_payload_invalido(self):
        """Garantiza que la capa de validación (Serializers) bloquee emails corruptos (400)."""
        payload_corrupto = {"email": "no_es_un_email"}
        response = self.client.post(self.url_registro, data=payload_corrupto, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('notificaciones.views.enviar_email_tarea.delay')
    def test_limite_de_peticiones_registro_throttling(self, mock_celery_task):
        """Prueba de estrés: Verifica el bloqueo del middleware ante ráfagas de peticiones (429)."""
        limite_maximo = 5
        
        for i in range(limite_maximo + 1):
            datos_dinamicos = {
                "email": f"dev_{i}@portfolio.com",
                "password": "SecurePassword123!"
            }
            response = self.client.post(self.url_registro, data=datos_dinamicos, format='json')
            
            if i < limite_maximo:
                self.assertEqual(
                    response.status_code, 
                    status.HTTP_201_CREATED, 
                    f"Falló en la petición {i+1}, se esperaba 201 y llegó {response.status_code}"
                )
            else:
                self.assertEqual(
                    response.status_code, 
                    status.HTTP_429_TOO_MANY_REQUESTS, 
                    "Se esperaba bloqueo por throttling (429) y la petición pasó"
                )
                

class IdempotenciaEmailTestCase(APITestCase):
    
    @patch('notificaciones.tasks.enviar_email_tarea.delay')
    def setUp(self, mock_task_delay):
        self.user = User.objects.create_user(username="cliente_test", password="cliente123")
        self.cliente = Cliente.objects.create(
            user=self.user, 
            email="idempotencia@gmail.com",
            estado_email_bienvenida=EstadoEmail.PENDIENTE
        )
        
    @patch('notificaciones.tasks.send_mail')
    def test_tarea_no_reenvia_email_si_ya_fue_enviado(self, mock_send_mail):
        """Verifica que ejecutar la tarea dos veces no repita el envío del email (Idempotencia)"""
        mock_send_mail.return_value = 1
    
        self.assertEqual(self.cliente.estado_email_bienvenida, EstadoEmail.PENDIENTE)
    
        resultado_1 = enviar_email_tarea(self.cliente.id)
        self.assertEqual(resultado_1, "Exito")
    
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.estado_email_bienvenida, EstadoEmail.ENVIADO)
    
        resultado_2 = enviar_email_tarea(self.cliente.id)
        self.assertEqual(resultado_2, "Ya estaba enviado")
    
        mock_send_mail.assert_called_once()


class ConcurrenciaEmailTestCase(TransactionTestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="concurrente_test", password="cliente123")
        self.cliente = Cliente.objects.create(
            user=self.user,
            email="concurrencia@gmail.com",
            estado_email_bienvenida=EstadoEmail.PENDIENTE
        )

    @patch('notificaciones.tasks.send_mail')
    def test_dos_workers_procesando_simultaneamente(self, mock_send_mail):
        mock_send_mail.return_value = 1
        client_id = self.cliente.id

        def tarea_envuelta(cid):
            try:
                return enviar_email_tarea(cid)
            finally:
                connection.close()  

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_1 = executor.submit(tarea_envuelta, client_id)
            future_2 = executor.submit(tarea_envuelta, client_id)
            
            resultado_1 = future_1.result()
            resultado_2 = future_2.result()

        resultados = {resultado_1, resultado_2}
        self.assertIn("Exito", resultados)
        self.assertIn("Ya estaba enviado", resultados)

        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.estado_email_bienvenida, EstadoEmail.ENVIADO)