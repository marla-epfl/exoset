from django import forms
from exoset.tag.models import TagProblemType, TagLevel, QuestionType, TagLevelResource, TagProblemTypeResource, \
    QuestionTypeResource, TagConcept
from exoset.ontology.models import Ontology, DocumentCategory
from exoset.document.models import LANGUAGES_CHOICES, Resource
from exoset.prerequisite.models import AssignPrerequisiteResource
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


class MetadataForm(forms.Form):
    language = forms.ChoiceField(
        required=True,
        label=_('Language'),
        widget=forms.RadioSelect,
        choices=LANGUAGES_CHOICES)
    title = forms.CharField(required=True, label=_('Title'), max_length=255)
    authors = forms.CharField(required=True, label=_('Author (Fond)'), max_length=255)
    difficulty_level = forms.ChoiceField(
        required=True,
        label=_('Difficulty level'),
        widget=forms.Select,
        choices=((x.pk, x.label) for x in TagLevel.objects.all())
    )
    question_type = forms.ChoiceField(
        required=False,
        label=_('Type of question'),
        widget=forms.Select,
        choices=((x.pk, x.label) for x in QuestionType.objects.all())
    )
    family_problem = forms.CharField(required=False, label=_('Family problem'), max_length=255)
    ontology0 = forms.ChoiceField(required=True, label=_('Ontology'), choices=((x.pk, x.name) for x in Ontology.objects.all()))
    ontology1 = forms.ChoiceField(required=False, label=_('Extra ontology'), choices=((x.pk, x.name) for x in Ontology.objects.all()))
    concept0 = forms.CharField(required=False, label=_("Concept"), max_length=255)
    concept1 = forms.CharField(required=False, label=_("Extra concept"), widget=forms.TextInput(
        attrs={
            'style': 'width: 400px',
            'class': 'basicAutoComplete',
            'data-url': "autocomplete_prerequisites/"
        }))
    concept2 = forms.CharField(required=False, label=_("Extra concept"), max_length=255)
    concept3 = forms.CharField(required=False, label=_("Extra concept"), max_length=255)
    concept4 = forms.CharField(required=False, label=_("Extra concept"), max_length=255)
    prerequisite0 = forms.CharField(required=False, label=_("Prerequisite"), widget=forms.TextInput(
        attrs={
            'url': '/admin_github/autocomplete_prerequisites',
            'id': 'prerequisite',
        }))
    prerequisite1 = forms.CharField(required=False, label=_("Extra prerequisite"), max_length=255)
    prerequisite2 = forms.CharField(required=False, label=_("Extra prerequisite"), max_length=255)
    prerequisite3 = forms.CharField(required=False, label=_("Extra prerequisite"), max_length=255)
    prerequisite4 = forms.CharField(required=False, label=_("Extra prerequisite"), max_length=255)

    def __init__(self, *args, **kwargs):
        """
        fill the form with existing data in database if existing
        """
        resource_id = kwargs.pop('id')
        folder_name = kwargs.pop('exercise_folder_name')
        super(MetadataForm, self).__init__(*args, **kwargs)
        if resource_id != 'None':
            # get data from database
            resource = Resource.objects.get(id=int(resource_id))
            title_exercise = resource.title
            level = TagLevelResource.objects.get(resource_id=resource.id).tag_level.id
            try:
                question = QuestionTypeResource.objects.get(resource_id=resource.pk).question_type.pk
            except QuestionTypeResource.DoesNotExist:
                question = ""
            try:
                tag_problem_type = TagProblemTypeResource.objects.get(resource_id=resource.pk).tag_problem_type.pk
            except TagProblemTypeResource.DoesNotExist:
                tag_problem_type = None
            concepts = TagConcept.objects.filter(resource_id=resource.pk)
            try:
                prerequisites = AssignPrerequisiteResource.objects.get(resource_id=resource.pk).prerequisite.all()
            except AssignPrerequisiteResource.DoesNotExist:
                prerequisites = None
            try:
                ontologies = DocumentCategory.objects.filter(resource_id=resource.pk)
            except DocumentCategory.DoesNotExist:
                ontologies = None
            self.fields['title'].initial = title_exercise
            self.fields['authors'].initial = resource.author
            self.fields['language'].initial = resource.language
            self.fields['difficulty_level'].initial = level
            self.fields['question_type'].initial = question
            self.fields['family_problem'].initial = tag_problem_type
            if concepts:
                i = 0
                for concept in concepts:
                    self.fields['concept' + str(i)].initial = concept.label
                    i += 1
            if prerequisites:
                y = 0
                for prerequisite in prerequisites:
                    self.fields['prerequisite' + str(y)].initial = prerequisite.label
                    y += 1
            if ontologies:
                index_ontologies = 0
                for ontology in ontologies:
                    self.fields['ontology' + str(index_ontologies)].initial = ontology.category.pk
                    index_ontologies += 1
