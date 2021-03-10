from rest_framework import serializers
from .models import Ontology, DocumentCategory


class OntologySerializers(serializers.ModelSerializer):
    class Meta:
        model = Ontology
        fields = ('id', 'name')


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ('resource', 'category')

