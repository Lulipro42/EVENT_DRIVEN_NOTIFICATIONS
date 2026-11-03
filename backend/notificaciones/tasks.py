import smtplib
from celery import shared_task
from django.db import transaction
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from notificaciones.models import Cliente, EstadoEmail


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError, OSError, smtplib.SMTPException, smtplib.SMTPServerDisconnected),
    retry_kwargs={'max_retries': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    throws=(ObjectDoesNotExist,)
)
def enviar_email_tarea(self, cliente_id):
    with transaction.atomic():
        cliente = Cliente.objects.select_for_update().get(id=cliente_id)
        
        if cliente.estado_email_bienvenida == EstadoEmail.ENVIADO:
            print(f"--- Email ya enviado previamente para cliente {cliente_id} ---")
            return "Ya estaba enviado"
        
        cliente.estado_email_bienvenida = EstadoEmail.EN_PROCESO
        cliente.save(update_fields=['estado_email_bienvenida'])
        
        try:
            enviados = send_mail(
                subject="¡Bienvenido a nuestra Fintech!",
                message=f"Hola, gracias por registrarte con el email {cliente.email}. Tu cuenta ha sido creada.",
                from_email=None,
                recipient_list=[cliente.email]
                )
        
            if enviados > 0:
                cliente.estado_email_bienvenida = EstadoEmail.ENVIADO
                cliente.save(update_fields=['estado_email_bienvenida'])
                print(f"--- Email enviado con exito a cliente {cliente_id}---")
                return "Exito"
            else:
                cliente.estado_email_bienvenida = EstadoEmail.FALLIDO
                cliente.save(update_fields=['estado_email_bienvenida'])
                raise smtplib.SMTPException("El servidor de correo no pudo entregar el mensaje (0 enviados).")
        except Exception as exc:
        
            cliente.estado_email_bienvenida = EstadoEmail.FALLIDO
            cliente.save(update_fields=['estado_email_bienvenida'])
            raise exc