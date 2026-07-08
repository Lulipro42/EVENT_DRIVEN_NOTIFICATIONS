# 🚀 API REST: Registro de Clientes (Event-Driven)
Este proyecto es una API profesional desarrollada en Django REST Framework, diseñada bajo una arquitectura de microservicios asíncronos para garantizar alta disponibilidad, seguridad y escalabilidad.

## 💎 Características Clave
*🏗️ **Arquitectura de Capas:** Separación total de responsabilidades (Views -> Services -> Serializers).

*⚡ **Asincronía Total:** Procesamiento de notificaciones mediante Celery + Redis, garantizando que el usuario no espere por correos.

*🛡️ **Seguridad Financiera/Datos:** Implementación de transaction.atomic() para asegurar la integridad absoluta en la base de datos.

*🔐 **Autenticación Robusta:** Integración con JWT (SimpleJWT) para sesiones seguras.

*🚧 **Control de Tráfico:** Protección mediante Throttling (5 peticiones/minuto para evitar spam).

**🔭 Observabilidad:** Dashboard con Flower para monitorear tareas en tiempo real.

### 🛠️ Tecnologías Utilizadas
**Backend:** Python 3.11 & Django 5.x

**API Toolkit:** Django REST Framework (DRF)

**Asincronía:** Celery & Redis

**Base de Datos:** PostgreSQLs

**Infraestructura:** Docker & Docker Compose

**Monitoreo:** Flower

### 📦 Instalación y Configuración (Docker)
Para levantar este proyecto, asegurate de tener instalado Docker Desktop.

1. Clonar el repositorio
