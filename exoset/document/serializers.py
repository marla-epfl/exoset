from rest_framework import serializers
from .models import Resource, Document


class ResourceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('id', 'title', 'author', 'description', 'date_creation', 'language', 'slug')


class DocumentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('uuid', 'document_type', 'language', 'resource', 'file')
