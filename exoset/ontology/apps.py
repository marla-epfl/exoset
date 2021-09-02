from django.apps import AppConfig
import vinaigrette


class OntologyConfig(AppConfig):
    name = 'exoset.ontology'

    def ready(self):
        from .models import Ontology  # or...
        # Register fields to translate
        vinaigrette.register(Ontology, ['name', 'description'])

