from django.apps import AppConfig
import vinaigrette


class TagConfig(AppConfig):
    name = 'exoset.tag'
    def ready(self):
        from .models import TagLevel, TagProblemType, QuestionType
        vinaigrette.register(TagLevel, ['label', 'difficulty_level'])
        vinaigrette.register(TagProblemType, ['label'])
        vinaigrette.register(QuestionType, ['label', 'description'])
