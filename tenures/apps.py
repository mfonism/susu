from django.apps import AppConfig


class TenuresConfig(AppConfig):
    name = 'tenures'

    def ready(self):
        import tenures.signals
