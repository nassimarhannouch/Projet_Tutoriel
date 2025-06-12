from django.apps import AppConfig


class AppcoursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appcours'

    def ready(self):
        import appcours.dashboard  # Importe ton dashboard pour qu'il s’enregistre
