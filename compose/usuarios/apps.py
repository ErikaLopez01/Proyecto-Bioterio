from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usuarios"

    def ready(self):
        # Importa señales después de cargar apps
        from . import signals  # noqa: F401
