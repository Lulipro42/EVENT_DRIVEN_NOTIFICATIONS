from notificaciones.serializers import ClienteSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

def custom_exception(exc, context):
    """
    Manejador global de excepciones personalizado.
    Estandariza las respuestas de error y asegura el loggeo de fallos 500 para CI/CD.
    """
    response = exception_handler(exc, context)
    

    if response is None:
        logger.error(f"Excepción no controlada en: {context['view'].__class__.__name__} - Error: {str(exc)}", exc_info=True)
        
        return Response ({
            "status":"error",
            "type":"ServerError",
            "message":"Ocurrio un error interno en el servirdo. Nuestro equipo esta trabajando en ello"
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    custom_response_data = {
        "status":"error",
        "type":exc.__class__.__name__,
        "message":"La solicitud no puede ser porcesada debido a un error de validacion o permisos",
        "error":response.data  
    }
    
    response.data = custom_response_data
    return response