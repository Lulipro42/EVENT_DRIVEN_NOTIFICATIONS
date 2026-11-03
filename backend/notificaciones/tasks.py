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
    try:
        with transaction.atomic():
            cliente = Cliente.objects.select_for_update().get(id=cliente_id)

            if cliente.estado_email_bienvenida == EstadoEmail.ENVIADO:
                print(f"--- Email ya enviado previamente para cliente {cliente_id} ---")
                return "Ya estaba enviado"
                
            if cliente.estado_email_bienvenida == EstadoEmail.EN_PROCESO:
                print(f"--- Email ya está siendo procesado para cliente {cliente_id} ---")
                return "Ya estaba enviado"

            cliente.estado_email_bienvenida = EstadoEmail.EN_PROCESO
            cliente.save(update_fields=['estado_email_bienvenida'])
            email_destino = cliente.email
            
    except ObjectDoesNotExist:
        print(f"--- El cliente con ID {cliente_id} no existe ---")
        raise
    except Exception as e:
        print(f"--- Error en fase de bloqueo para cliente {cliente_id}: {e} ---")
        raise e

    try:
        enviados = send_mail(
            subject="¡Bienvenido a nuestra Fintech!",
            message=f"Hola, gracias por registrarte con el email {email_destino}. Tu cuenta ha sido creada.",
            from_email=None,
            recipient_list=[email_destino]
        )
        
        if enviados > 0:
            Cliente.objects.filter(id=cliente_id).update(estado_email_bienvenida=EstadoEmail.ENVIADO)
            print(f"--- Email enviado con exito a cliente {cliente_id} ---")
            return "Exito"
        else:
            raise smtplib.SMTPException("El servidor de correo no pudo entregar el mensaje (0 enviados).")

    except Exception as exc:
        Cliente.objects.filter(id=cliente_id).update(estado_email_bienvenida=EstadoEmail.FALLIDO)
        print(f"--- Falló el envío de email para cliente {cliente_id}: {exc} ---")
        raise exc