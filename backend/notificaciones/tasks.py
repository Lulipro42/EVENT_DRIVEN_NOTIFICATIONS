from celery import shared_task
import time
from notificaciones.models import Cliente

# Esta es la única función que necesitas.
# Configurada con 'bind=True' para permitir el manejo de estados de la tarea.
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
    retry_backoff=True,
    retry_backoff_max=600
)
def enviar_email_tarea(self, cliente_id):
    cliente = Cliente.objects.get(id=cliente_id)
    print(f"--- Iniciando envío de email para el cliente ID: {cliente_id} ---")
    
    # 2. Código que solo se ejecutará si NO lanzamos el error
    time.sleep(2)
    print(f"--- Éxito ---")
    return "Éxito"