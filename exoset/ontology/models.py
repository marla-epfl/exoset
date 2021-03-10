from django.db import models
from treebeard.mp_tree import MP_Node
from exoset.document.models import Resource


class Ontology(MP_Node):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    node_order_by = ['name']

    def __str__(self):
        return self.name


class DocumentCategory(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    category = models.ForeignKey(Ontology, on_delete=models.CASCADE)

    def ontology_tree(self):
        return self.category.get_ancestors()

    def __str__(self):
        return self.category.name + " " + self.resource.title

