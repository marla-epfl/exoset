from django.apps import AppConfig


class PrerequisiteConfig(AppConfig):
    name = "exoset.prerequisite"
    verbose_name = "Prerequisite"

    def ready(self):
        try:
            import exoset.prerequisite.signals  # noqa F401
        except ImportError:
            pass
