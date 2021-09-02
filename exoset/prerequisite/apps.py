from django.apps import AppConfig
import vinaigrette

class PrerequisiteConfig(AppConfig):
    name = "exoset.prerequisite"
    verbose_name = "Prerequisite"

    def ready(self):
        try:
            import exoset.prerequisite.signals  # noqa F401
        except ImportError:
            pass
        from .models import Prerequisite  # or...
        # Register fields to translate
        vinaigrette.register(Prerequisite, ['domain', 'label'])
