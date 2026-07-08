import os
from celery import Celery

# Como el working_dir es /app/backend, la raíz es 'config'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Esto busca la configuración en tu settings.py de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Esto busca las tareas automáticamente en tus apps
app.autodiscover_tasks()