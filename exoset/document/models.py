import uuid

from django.db import models
from django.core.files import File
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib.auth import get_user_model
# Create your models here.
from .literals import DEFAULT_LANGUAGE, DEFAULT_LANGUAGE_CODES


User = get_user_model()

FR = "FRANÇAIS"
IT = "ITALIANO"
EN = "ENGLISH"

LANGUAGES_CHOICES = (
        (FR, "Français"),
        (IT, "Italiano"),
        (EN, "English"),
    )


class Resource(models.Model):
    EXOSET = "EXOSET"
    EXTERNAL = "EXTERNAL"
    LIBRARY_CHOICES = (
        (EXOSET, _("Exoset")),
        (EXTERNAL, _("External"))
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    visible = models.BooleanField(default=True)
    date_creation = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=250)
    library = models.CharField(max_length=8, choices=LIBRARY_CHOICES, default=EXOSET)
    language = models.CharField(max_length=8, choices=LANGUAGES_CHOICES, default=FR)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Resource, self).save(*args, **kwargs)


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
    file = models.FileField(upload_to='document/')
