# No olvides importar los modelos y tareas necesarios aquí arriba
from .models import Cliente
from .tasks import enviar_email_tarea

def crear_nuevo_cliente(datos_validos):
    # 1. Limpiamos el email
    email_limpio = datos_validos.get('email','').lower().strip()
    
    # 2. Creamos el objeto (usando **datos_validados para desempaquetar el resto de campos)
    # Nota: Si también necesitas guardar el 'user' o 'password', agrégalos aquí.
    nuevo_objeto = Cliente.objects.create(
        email=email_limpio,
        user=datos_validos.get('user'),
        password=datos_validos.get('password'),
        
    )
    
    # 3. Disparamos la tarea (¡con paréntesis!)
    enviar_email_tarea.delay(email_limpio)
    
    return nuevo_objeto
    
HOY 05/07/2026 me costo hacer eso solo a la hora de escribir la sintaxys porque luego a la hora de comprenderlo no 