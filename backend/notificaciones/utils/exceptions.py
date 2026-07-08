from notificaciones.serializers import ClienteSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

def custom_exception(exc, context): # Bueno aca viendo el api-guide de django se me vino a la mente algo asi, perdon si esta mal 
    """
    Manejador global de excepciones personalizado.
    Estandariza las respuestas de error y asegura el loggeo de fallos 500 para CI/CD.
    """
    # 1. Dejamos que DRF intente manejar la excepción primero (400, 401, 403, 404, 429)
    response = exception_handler(exc, context)
    
    # 2. ESCENARIO A: Error inesperado del servidor (Bug de código, caída de BD, etc.)
    if response is None:
        # CRITERIO DE INGENIERÍA: Registramos el error real en los logs del sistema
        # Esto es vital para depurar fallos en producción sin exponer datos sensibles al cliente.
        logger.error(f"Excepción no controlada en: {context['view'].__class__.__name__} - Error: {str(exc)}", exc_info=True)
        
        return Response ({
            "status":"error",
            "type":"ServerError",
            "message":"Ocurrio un error interno en el servirdo. Nuestro equipo esta trabajando en ello"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # 3. ESCENARIO B: Errores controlados por DRF (Ej: Validación de Serializers, Throttling)
    # Estandarizamos la respuesta para que el Frontend siempre lea la misma estructura.
    custom_response_data = {
        "status":"error",
        "type":exc.__class__.__name__,
        "message":"La solicitud no puede ser porcesada debido a un error de validacion o permisos",
        "error":response.data  # Mantiene los mensajes originales de Django (ej: 'Este campo es obligatorio')
    }
    
    response.data = custom_response_data
    return response