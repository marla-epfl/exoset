from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
# Register your models here.
from .models import TagLevel, TagConcept, TagProblemType, TagLevelResource, TagProblemTypeResource, QuestionType, \
    QuestionTypeResource


@register(TagLevel)
class TagLevelAdmin(ModelAdmin):
    list_display = ['label',]
    verbose_name = _('Level')
    verbose_name_plural = _('Levels')


@register(TagConcept)
class TagConceptAdmin(ModelAdmin):
    list_display = ['label', ]
    verbose_name = _('Concept')
    verbose_name_plural = _('Concepts')


@register(TagProblemType)
class TagProblemTypeAdmin(ModelAdmin):
    list_display = ['label', ]
    verbose_name = _('Family problem')
    verbose_name_plural = _('Family problems')


@register(TagLevelResource)
class TagLevelResourceAdmin(ModelAdmin):
    list_display = ['tag_level',]
    verbose_name = _('Resource level')
    verbose_name_plural = _('Resources levels')


@register(TagProblemTypeResource)
class TagProblemTypeResourceAdmin(ModelAdmin):
    list_display = ['tag_problem_type', 'resource']
    verbose_name = _('Problem type Resource link')
    verbose_name_plural = _('Problem types resources links')


@register(QuestionType)
class QuestionTypeAdmin(ModelAdmin):
    list_display = ['label', 'description']
    verbose_name = _('Question type')
    verbose_name_plural = _('PQuestion types')


@register(QuestionTypeResource)
class QuestionTypeResourceAdmin(ModelAdmin):
    list_display = ['question_type', 'resource']
    verbose_name = _('Question type Resource link')
    verbose_name_plural = _('Question types resources links')
