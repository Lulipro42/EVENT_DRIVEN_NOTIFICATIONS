from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cliente
from notificaciones.tasks import enviar_email_tarea

@receiver(post_save, sender=Cliente)
def notificaiones(sender,instance,created,**kwargs):
    
    if created: # Aca el created es true solo si el cliente se acaba de registrar
        
        enviar_email_tarea.delay(instance.id)  # 3. Disparamos la tarea de Celery pasando el ID del nuevo cliente