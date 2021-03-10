from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
# Register your models here.
from .models import Resource, Document


@register(Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ['title', ]
    verbose_name = _('Resource')
    verbose_name_plural = _('Resources')


@register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ['uuid', ]
    verbose_name = _('Resource')
    verbose_name_plural = _('Resources')
