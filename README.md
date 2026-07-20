# 🚀 API REST: Registro de Clientes (Event-Driven)

Este proyecto es una API profesional desarrollada en Django REST Framework, diseñada bajo una arquitectura de microservicios asíncronos para garantizar alta disponibilidad, seguridad y escalabilidad.

## 💎 Características Clave

* 🏗️ **Arquitectura de Capas:** Separación total de responsabilidades (Views -> Services -> Serializers).
* ⚡ **Asincronía Total:** Procesamiento de notificaciones mediante Celery + Redis, garantizando que el usuario no espere por correos.
* 🛡️ **Seguridad Financiera/Datos:** Implementación de `transaction.atomic()` para asegurar la integridad absoluta en la base de datos.
* 🔐 **Autenticación Robusta:** Integración con JWT (SimpleJWT) para sesiones seguras.
* 🚧 **Control de Tráfico:** Protección mediante Throttling (5 peticiones/minuto para evitar spam).
* 🔭 **Observabilidad:** Dashboard con Flower para monitorear tareas en tiempo real.
* 🔁 **Resiliencia ante fallos:** Tareas configuradas con `acks_late` y reintentos con backoff exponencial, para que ninguna notificación se pierda si un worker cae a mitad de proceso.
* 🎯 **Idempotencia:** Cada tarea verifica su propio estado antes de ejecutarse, evitando el envío duplicado de notificaciones aunque Celery reintente la operación.

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.11 & Django 5.x
- **API Toolkit:** Django REST Framework (DRF)
- **Asincronía:** Celery & Redis
- **Base de Datos:** PostgreSQL
- **Infraestructura:** Docker & Docker Compose
- **Monitoreo:** Flower

## 📦 Instalación y Configuración (Docker)

Para levantar este proyecto, asegurate de tener instalado Docker Desktop.

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/Lulipro42/EVENT_DRIVEN_NOTIFICATIONS.git
   cd EVENT_DRIVEN_NOTIFICATIONS
   ```

2. **Levantar el ecosistema:**

   ```bash
   docker-compose up --build
   ```

3. **Monitoreo en tiempo real:**

   Accedé a `http://localhost:5555` para ver el estado de tus tareas en Flower.

## 🧪 Testing Profesional

Ejecutá el siguiente comando para validar que tu lógica sigue siendo infalible:

```bash
docker-compose exec web python manage.py test
```

## 🔧 Decisiones técnicas de resiliencia (Celery)

Estas son las configuraciones puntuales que hacen que el sistema de notificaciones sea confiable en escenarios reales, no solo en el camino feliz:

### `acks_late` + `task_reject_on_worker_lost`

Por defecto, Celery marca una tarea como "completada" en el broker (Redis) apenas el worker la toma, no cuando termina de ejecutarla. Esto significa que si el worker muere a mitad de camino (crash, reinicio, `kill -9`), la tarea se pierde silenciosamente — el email nunca se manda y nadie se entera.

Con `CELERY_TASK_ACKS_LATE = True`, la tarea solo se confirma como completada **después** de ejecutarse con éxito. Si el worker muere antes de eso, la tarea vuelve a la cola y otro worker la retoma. `CELERY_TASK_REJECT_ON_WORKER_LOST = True` refuerza esto: si Celery detecta que el worker murió, rechaza explícitamente la tarea para que vuelva a la cola en vez de quedar en un estado ambiguo.

### Idempotencia en `enviar_email_tarea`

`acks_late` protege contra **perder** una tarea, pero no contra **duplicarla**: si el worker manda el email y muere justo antes de confirmarlo a Redis, la tarea se reintenta y el email se manda dos veces.

Para evitar esto, el modelo `Cliente` tiene un campo `email_bienvenida_enviado` (booleano). Antes de ejecutar el envío, la tarea chequea ese campo — si ya está en `True`, corta ahí mismo sin repetir la operación. Recién después de un envío exitoso, lo marca en `True` y guarda. Esto hace que la tarea sea segura de ejecutar más de una vez con el mismo resultado.

### Retry con backoff exponencial

Las excepciones transitorias de red (`ConnectionError`, `TimeoutError`, `OSError`) disparan reintentos automáticos, con un intervalo que crece exponencialmente entre intentos (hasta un máximo de 600 segundos). Esto evita que, ante una falla temporal del servicio de email, el sistema martille reintentos inmediatos sin dar tiempo a que el problema se resuelva. Errores de programación (`TypeError`, `AttributeError`, etc.) quedan fuera de este mecanismo a propósito, para que fallen de inmediato y sean visibles en los logs, en vez de ocultarse detrás de reintentos.

## 💡 Lecciones Aprendidas (El valor del Ingeniero)

- **Desacoplamiento:** Cómo delegar tareas pesadas a un worker para mejorar la experiencia de usuario (UX).
- **Atomicidad:** La importancia de proteger la BD contra estados inconsistentes.
- **Resiliencia:** La diferencia entre una tarea que "funciona" en el camino feliz y una que sobrevive a fallos reales de infraestructura (workers que mueren, reintentos, duplicados).
- **Observabilidad:** La diferencia entre "código que corre" y "código que puedo monitorear".

---

Desarrollado con arquitectura orientada a eventos para el máximo rendimiento.