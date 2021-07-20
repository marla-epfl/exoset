from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
# Register your models here.
from .models import GitHubRepository


@register(GitHubRepository)
class GitHubRepositoryAdmin(ModelAdmin):
    list_display = ['repository_name', ]
    verbose_name = _('GitHub repository')
    verbose_name_plural = _('GitHub Repositories')

