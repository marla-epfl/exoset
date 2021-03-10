from rest_framework import serializers
from .models import TagLevel, TagProblemType


class TagLevelSerializers(serializers.ModelSerializer):
    class Meta:
        model = TagLevel
        fields = ('label', 'difficulty')


class TagProblemTypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = TagProblemType
        fields = ('label',)
