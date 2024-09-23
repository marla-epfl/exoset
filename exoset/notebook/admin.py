from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
# Register your models here.
from .models import GitRepository, Notebook


@register(GitRepository)
class GitRepositoryAdmin(ModelAdmin):
    list_display = ['title', 'course', 'teacher']
    verbose_name = _('GitRepository')
    verbose_name_plural = _('GitRepositories')


@register(Notebook)
class NotebookAdmin(ModelAdmin):
    list_display = ['title', 'git_repository', 'html_view', 'slug']
    verbose_name = _('Notebook')
    verbose_name_plural = _('Notebooks')

