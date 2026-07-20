from celery import shared_task
import time
from django.core.mail import send_mail
from notificaciones.models import Cliente

# Esta es la única función que necesitas.
# Configurada con 'bind=True' para permitir el manejo de estados de la tarea.
@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError, OSError),
    retry_kwargs={'max_retries': 5},
    retry_backoff=True,
    retry_backoff_max=600
)
def enviar_email_tarea(self, cliente_id):
    cliente = Cliente.objects.get(id=cliente_id)
    print(f"--- Iniciando envío de email para el cliente ID: {cliente_id} ---")
    
    if cliente.email_bienvenida_enviado:
        print(F"--- Email ya enviado antes para cliente {cliente_id}, no se repite--")
        return "Ya estaba enviado"
    
    print(f"--- Iniciando envío de email para el cliente ID: {cliente_id} ---")
    # 2. Código que solo se ejecutará si NO lanzamos el error
    send_mail(
        subject="!Bienvenido a nuestra Fintech!",
        message=f"Hola, gracias por registrarte con el email {cliente.email}. tu cuenta ha sido creada",
        from_email=None,
        recipient_list=[cliente.email]
    )
    
    
    cliente.email_bienvenida_enviado = True
    cliente.save()
    
    print(f"--- Éxito ---")
    return "Éxito"