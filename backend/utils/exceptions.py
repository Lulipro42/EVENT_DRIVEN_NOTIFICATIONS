import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


logger = logging.getLogger(__name__)

def custom_exception(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.error(f"Excepción no controlada en: {context['view'].__class__.__name__} - Error: {str(exc)}", exc_info=True)
        
        return Response({
            "status": "error",
            "type": "ServerError",
            "message": "Ocurrió un error interno en el servidor. Nuestro equipo técnico ya fue notificado."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    custom_response_data = {
        "status": "error",
        "type": exc.__class__.__name__,
        "message": "La solicitud no pudo ser procesada debido a un error de validación o permisos.",
        "errors": response.data
    }
    
    response.data = custom_response_data
    return response