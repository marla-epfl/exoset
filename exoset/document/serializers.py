from rest_framework import serializers
from .models import Resource, Document


class ResourceSerializers(serializers.ModelSerializer):
    date_creation = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Resource
        fields = ('id', 'title', 'author', 'description', 'date_creation', 'language', 'slug', 'ontology_path',
                  'tag_concept', 'family_problem', 'related_courses', 'prerequisite_assigned', 'tag_level',
                  'tag_exercise_type',)


class DocumentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('uuid', 'document_type', 'language', 'resource', 'file')
