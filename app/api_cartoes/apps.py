from django.apps import AppConfig


class ApiCartoesConfig(AppConfig):
    name = 'api_cartoes'
    verbose_name = 'Cartões'

    def ready(self):
        from . import signals
