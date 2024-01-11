from django.apps import AppConfig


class GraphapiConfig(AppConfig):
    name = 'exoset.graphapi'
    verbose_name = "Graphapi"

    def ready(self):
        try:
            import exoset.githubadmin.signals  # noqa F401
        except ImportError:
            pass

