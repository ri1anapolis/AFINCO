# pylint: disable=missing-module-docstring,missing-class-docstring,import-outside-toplevel,unused-import
from django.apps import AppConfig


class DepositosConfig(AppConfig):
    name = "depositos"

    def ready(self):
        from . import signals
