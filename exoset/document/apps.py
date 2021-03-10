from django.apps import AppConfig


class DocumentConfig(AppConfig):
    name = "exoset.document"
    verbose_name = "Document"

    def ready(self):
        try:
            import exoset.document.signals  # noqa F401
        except ImportError:
            pass
