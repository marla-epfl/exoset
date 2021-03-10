from django.contrib.admin import ModelAdmin, register
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Ontology, DocumentCategory


@register(Ontology)
class OntologyAdmin(TreeAdmin):
    form = movenodeform_factory(Ontology)


@register(DocumentCategory)
class DocumentCategoryAdmin(ModelAdmin):
    list_display = ('resource', 'category')

