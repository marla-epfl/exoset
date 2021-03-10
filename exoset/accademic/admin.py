from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
# Register your models here.
from .models import Course, Sector


@register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ['sector', ]
    verbose_name = _('Course')
    verbose_name_plural = _('Courses')


@register(Sector)
class SectorAdmin(ModelAdmin):
    list_display = ['name', ]
    verbose_name = _('Sector')
    verbose_name_plural = _('Sectors')
