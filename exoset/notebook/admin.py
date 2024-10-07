from django.contrib.admin import ModelAdmin, register
from django.utils.translation import gettext as _
# Register your models here.
from .models import GitRepository, Notebook, Kernel, NBType, TagConceptNotebook, TagConceptNotebookEntry


@register(Kernel)
class KernelAdmin(ModelAdmin):
    list_display = ['name']
    verbose_name = _('Kernel')
    verbose_name_plural = _('Kernels')


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


@register(NBType)
class NBTypeAdmin(ModelAdmin):
    list_display = ['name']
    verbose_name = _('Notebook type')
    verbose_name_plural = _('Notebook types')


@register(TagConceptNotebook)
class TagConceptNotebookAdmin(ModelAdmin):
    list_display = ['concept_name', 'wiki_id']
    verbose_name = _('Notebook concept')
    verbose_name_plural = _('Notebook concepts')


@register(TagConceptNotebookEntry)
class TagConceptNotebookEntryAdmin(ModelAdmin):
    list_display = ['notebook', 'tag_concept']
    verbose_name = _('Notebook concept entry')
    verbose_name_plural = _('Notebook concept Entries')
