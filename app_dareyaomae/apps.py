from django.db import connection
from django.apps import AppConfig
from django.db.backends.signals import connection_created

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dareyaomae'
