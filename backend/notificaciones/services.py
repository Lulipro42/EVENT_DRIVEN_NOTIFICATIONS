# No olvides importar los modelos y tareas necesarios aquí arriba
from .models import Cliente
import logging
from .tasks import enviar_email_tarea
from django.db import transaction
from .serializers import ClienteSerializer
logger = logging.getLogger(__name__)

def procesar_registro_exitoso(cliente):
    def dispara_tarea():
        try:
            enviar_email_tarea.delay(cliente.id)
        except Exception as e:
            # Si Celery falla, el usuario ya se creó, así que no borramos al usuario.
            # Pero logueamos el error para que vos te enteres en los logs.
            logger.error(f"Fallo al disparar tarea para el cliente {cliente.id}: {e}")
            
    transaction.on_commit(dispara_tarea)