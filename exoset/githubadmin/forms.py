from django import forms
from exoset.tag.models import TagProblemType, TagLevel, QuestionType, TagLevelResource, TagProblemTypeResource, \
    QuestionTypeResource, TagConcept
from exoset.ontology.models import Ontology, DocumentCategory
from exoset.document.models import LANGUAGES_CHOICES, Resource
from exoset.prerequisite.models import AssignPrerequisiteResource
from django.utils.translation import ugettext_lazy as _
from exoset.accademic.models import Sector, Course

VISIBLE_CHOICES = [(1, _('Yes')), (0, _('No'))]


def query_set_root_children():
    children = []
    roots = Ontology.get_root_nodes()
    for x in roots:
        children += x.get_children()
    return children


def query_set_parent_children():
    children = []
    roots = query_set_root_children()
    for x in roots:
        children += x.get_children()
    return children


choices_root = [(x.pk, _(x.name)) for x in Ontology.get_root_nodes()]
choices_root.insert(0, (None, '-----'))

choices_parent = [(x.pk, _(x.name)) for x in query_set_root_children()]
choices_parent.insert(0, (None, '-----'))

choices_children = [(x.pk, _(x.name)) for x in query_set_parent_children()]
choices_children.insert(0, (None, '-----'))

choices_cour = [(x.pk, _(x.name)) for x in Sector.objects.all()]
choices_cour.insert(0, (None, '-----'))


class MetadataForm(forms.Form):
    language = forms.ChoiceField(
        required=True,
        label=_('Language'),
        widget=forms.Select,
        choices=LANGUAGES_CHOICES)
    title = forms.CharField(required=True, label=_('Title*'), max_length=255)
    authors = forms.CharField(required=True, label=_('Collection*'), max_length=255)
    difficulty_level = forms.ChoiceField(
        required=True,
        label=_('Difficulty level*'),
        widget=forms.Select,
        choices=((x.pk, _(x.label)) for x in TagLevel.objects.all())
    )
    question_type = forms.ChoiceField(
        required=False,
        label=_('Type of question'),
        widget=forms.Select,
        choices=((x.pk, _(x.label)) for x in QuestionType.objects.all())
    )
    class_type = forms.ChoiceField(
        required=False,
        label=_('Class'),
        widget=forms.Select,
        choices=choices_cour
    )
    family_problem = forms.CharField(required=False, label=_('Family problem'), max_length=255)
    root_ontology0 = forms.ChoiceField(required=True, label=_('Ontology*'), choices=choices_root,
                                       widget=forms.Select(attrs={'class': 'root_ontology_input',
                                                                  'data-line': '0'}))
    parent_ontology0 = forms.ChoiceField(required=True, label='', choices=choices_parent,
                                         widget=forms.Select(attrs={'class': 'parent_ontology_input',
                                                                    'data-line': '0'}))
    ontology0 = forms.ChoiceField(required=True, label='', choices=choices_children,
                                  widget=forms.Select(attrs={'class': 'ontology_input',
                                                             'data-line': '0'}))
    root_ontology1 = forms.ChoiceField(required=False, label=_('Extra ontology'), choices=choices_root,
                                       widget=forms.Select(attrs={'class': 'root_ontology_input',
                                                                  'data-line': '1'}))
    parent_ontology1 = forms.ChoiceField(required=False, label='', choices=choices_parent,
                                         widget=forms.Select(attrs={'class': 'parent_ontology_input',
                                                                    'data-line': '1'}))
    ontology1 = forms.ChoiceField(required=False, label='', choices=choices_children,
                                  widget=forms.Select(attrs={'class': 'ontology_input',
                                                             'data-line': '1'}))
    concept0 = forms.CharField(required=False, label=_("Concept"), max_length=255, widget=forms.TextInput(
        attrs={'url': '/admin_github/autocomplete_concepts',
               'id': 'concept0',
               'class': 'concepts',
               }))
    concept1 = forms.CharField(required=False, label=_("Extra concept"), widget=forms.TextInput(
        attrs={'url': '/admin_github/autocomplete_concepts',
               'id': 'concept1',
               'class': 'concepts',
               }))
    concept2 = forms.CharField(required=False, label=_("Extra concept"), max_length=255, widget=forms.TextInput(
        attrs={'url': '/admin_github/autocomplete_concepts',
               'id': 'concept2',
               'class': 'concepts',
               }))
    concept3 = forms.CharField(required=False, label=_("Extra concept"), max_length=255, widget=forms.TextInput(
        attrs={'url': '/admin_github/autocomplete_concepts',
               'id': 'concept3',
               'class': 'concepts',
               }))
    concept4 = forms.CharField(required=False, label=_("Extra concept"), max_length=255, widget=forms.TextInput(
        attrs={'url': '/admin_github/autocomplete_concepts',
               'id': 'concept4',
               'class': 'concepts',
               }))
    prerequisite0 = forms.CharField(required=False, label=_("Prerequisite"), widget=forms.TextInput(
        attrs={
            'url': '/admin_github/autocomplete_concepts',
            'id': 'prerequisite0',
            'class': 'prerequisites',
        }))
    prerequisite1 = forms.CharField(required=False, label=_("Extra prerequisite"), widget=forms.TextInput(
        attrs={
            'url': '/admin_github/autocomplete_concepts',
            'id': 'prerequisite1',
            'class': 'prerequisites',
        }))
    prerequisite2 = forms.CharField(required=False, label=_("Extra prerequisite"), widget=forms.TextInput(
        attrs={
            'url': '/admin_github/autocomplete_concepts',
            'id': 'prerequisite2',
            'class': 'prerequisites',
        }))
    prerequisite3 = forms.CharField(required=False, label=_("Extra prerequisite"), widget=forms.TextInput(
        attrs={
            'url': '/admin_github/autocomplete_concepts',
            'id': 'prerequisite3',
            'class': 'prerequisites',
        }))
    prerequisite4 = forms.CharField(required=False, label=_("Extra prerequisite"), widget=forms.TextInput(
        attrs={
            'url': '/admin_github/autocomplete_concepts',
            'id': 'prerequisite4',
            'class': 'prerequisites',
        }))

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
                tag_problem_type = TagProblemTypeResource.objects.get(resource_id=resource.pk).tag_problem_type
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
            try:
                sector = Course.objects.get(resource=resource).sector.id
            except Course.DoesNotExist:
                sector = None
            self.fields['title'].initial = title_exercise
            self.fields['authors'].initial = resource.author
            self.fields['language'].initial = resource.language
            self.fields['difficulty_level'].initial = level
            self.fields['question_type'].initial = question
            self.fields['family_problem'].initial = tag_problem_type
            self.fields['class_type'].initial = sector
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
                    self.fields['root_ontology' + str(index_ontologies)].initial = ontology.category.get_root().id
                    self.fields['parent_ontology' + str(index_ontologies)].initial = ontology.category.get_parent().id
                    self.fields['ontology' + str(index_ontologies)].initial = ontology.category.id
                    index_ontologies += 1
                    if index_ontologies >= 2:
                        break


class ResourceForm(forms.Form):
    visible = forms.ChoiceField(choices=VISIBLE_CHOICES, widget=forms.RadioSelect)


class FlagForm(forms.Form):
    flag_resource = forms.ChoiceField(choices=Resource.FLAG_CHOICES)
