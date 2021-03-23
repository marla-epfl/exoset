from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
from .models import Prerequisite, AssignPrerequisiteResource


@register(Prerequisite)
class PrerequisiteAdmin(ModelAdmin):
    list_display = ['label', ]
    verbose_name = _('Prerequisite')
    verbose_name_plural = _('Prerequisites')


@register(AssignPrerequisiteResource)
class AssignPrerequisiteResourceAdmin(ModelAdmin):
    list_display = ['resource', ]
    verbose_name = _('Link resource prerequisite')
    verbose_name_plural = _('Links resource prerequisite')
