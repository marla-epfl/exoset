import uuid

from django.db import models

from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.contrib.auth import get_user_model
# Create your models here.
import os
import random
import string
from os.path import splitext
from django.dispatch import receiver
from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage

User = get_user_model()

FR = "FRANÇAIS"
IT = "ITALIANO"
EN = "ENGLISH"

LANGUAGES_CHOICES = (
        (FR, "Français"),
        #(IT, "Italiano"),
        (EN, "English"),
    )


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, max_length)


def update_filename(instance, filename):
    path = "document/"
    file_extension = splitext(filename)[1][1:].lower()
    new_file_name = str(instance.uuid) + "." + file_extension
    return os.path.join(path, new_file_name)


class Resource(models.Model):
    EXOSET = "EXOSET"
    EXTERNAL = "EXTERNAL"
    LIBRARY_CHOICES = (
        (EXOSET, _("Exoset")),
        (EXTERNAL, _("External"))
    )
    RVMD = "REVISEMD"
    RVF = "REVISEFILE"
    OB = "OBSOLETE"
    FLAG_CHOICES = (
        (RVMD, _("Revise metadata")),
        (RVF, _("Revise files")),
        (OB, _("Obsolete"))
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    visible = models.BooleanField(default=False)
    date_creation = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=250)
    library = models.CharField(max_length=8, choices=LIBRARY_CHOICES, default=EXOSET)
    language = models.CharField(max_length=8, choices=LANGUAGES_CHOICES, default=FR)
    flag = models.CharField(max_length=20, choices=FLAG_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        slugs_list = Resource.objects.values_list('slug', flat=True)
        suffix_slug = ''
        if self.slug in slugs_list:
            suffix_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.slug += suffix_slug
        super(Resource, self).save(*args, **kwargs)

    @property
    def ontology_path(self):
        list_ontology = self.documentcategory_set.values_list('category__name', flat=True)
        ontology_path = ""
        for ontology in list_ontology:
            ontology_path += _(ontology) + " "
        return ontology_path

    @property
    def tag_concept(self):
        list_concepts = self.tagconcept_set.values_list('label', flat=True)
        concept_path = ""
        for concept in list_concepts:
            concept_path += concept + " "
        return list_concepts

    @property
    def family_problem(self):
        list_family_problem = self.tagproblemtyperesource_set.values_list('tag_problem_type__label', flat=True)
        tag_problem_type_path = ""
        for tag_problem_type in list_family_problem:
            tag_problem_type_path += _(tag_problem_type) + " "
        return tag_problem_type_path

    @property
    def prerequisite_assigned(self):
        list_prerequisite = self.assignprerequisiteresource_set.values_list('prerequisite__label', flat=True)
        prerequisite_path = ""
        for prerequisite in list_prerequisite:
            prerequisite_path += _(prerequisite) + " "
        return prerequisite_path

    @property
    def related_courses(self):
        list_related_courses = self.course_set.values_list('sector__name', 'semester')
        related_courses_path = ""
        for related_course in list_related_courses:
            this_related_class = _(''.join(related_course[0]))
            related_courses_path += this_related_class + " "
        return related_courses_path

    @property
    def tag_level(self):
        level_tag = self.taglevelresource_set.values_list('tag_level__label')
        if level_tag:
            new_tag_level = ''.join(level_tag[0])
            level_tag = _(new_tag_level)
        else:
            level_tag = ""
        return level_tag

    @property
    def tag_question_type(self):
        tag_question_type = self.questiontyperesource_set.values_list('question_type__label')
        question_type = ""
        if tag_question_type:
            this_question_type = _(''.join(tag_question_type[0]))
            question_type = this_question_type
        return question_type

    @property
    def missing_fields_resource(self):
        dict_metadata = dict({'ontology': self.ontology_path,
                              'concept': self.tag_concept,
                              'family_problem': self.family_problem,
                              'prerequisite': self.prerequisite_assigned,
                              'class_type': self.related_courses,
                              'question_type': self.tag_question_type})
        missing_field = {k for k, v in dict_metadata.items() if not v}
        return missing_field


class Document(models.Model):
    STAT = _("STATEMENT")
    SOL = _("SOLUTION")
    APP = _("APPENDIX")
    EXT = _("EXTRA")

    DOCTYPE_CHOICES = (
        (STAT, _("Statement")),
        (SOL, _("Solution")),
        (APP, _("Appendix")),
        (EXT, _("Extra")),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=9, choices=DOCTYPE_CHOICES)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    language = models.CharField(max_length=8, choices=LANGUAGES_CHOICES, blank=True, null=True)
    file = models.FileField(upload_to=update_filename, storage=OverwriteStorage())

    class Meta:
        constraints = [models.UniqueConstraint(fields=['document_type', 'resource'],
                                               condition=models.Q(document_type='STATEMENT'),
                                               name='unique_statement_resource'),
                       models.UniqueConstraint(fields=['document_type', 'resource'],
                                               condition=models.Q(document_type='SOLUTION'),
                                               name='unique_solution_resource')]


class ResourceSourceFile(models.Model):
    """
    class to link the resources to the source code. The directory shown should be synchronized with the
    gitHub repository
    """
    resource = models.OneToOneField(Resource, on_delete=models.CASCADE)
    source = models.FilePathField(path=settings.MEDIA_ROOT + "/github/" + settings.GITHUB_REPO_NAME, allow_files=False,
                                  allow_folders=True, max_length=255)
    style = models.FilePathField(path=settings.MEDIA_ROOT + "/github/" + settings.GITHUB_REPO_NAME, allow_folders=True,
                                 null=True, blank=True, max_length=255)

    @property
    def resource_visible(self):
        """
        determines if the resource is visible on the exoset web platform
        """
        return self.resource.visible

    @property
    def file_name(self):
        """
        return the name of the exercise without the path
        """
        try:
            exercise_name = self.source.rsplit('/', 1)[1]
        except IndexError:
            exercise_name = "Name not found"
        return exercise_name

    class Meta:
        constraints = [models.UniqueConstraint(fields=['source', 'style'], name='different_source_style')]
