from colorfield.fields import ColorField
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from exoset.document.models import Resource
# Create your models here.


class TagLevel(models.Model):
    """
    class for tag level
    """
    EX = "EXAM"
    CH = "CHALLENGE"
    TR = "TRAINING"
    ST = "STANDARD"
    LEVEL_CHOICES = (
        (EX, _("Exam")),
        (CH, _("Challenge")),
        (TR, _("Training")),
        (ST, _("Standard")),
    )
    label = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=9, choices=LEVEL_CHOICES, default=TR)
    color = ColorField(default='#FF0000')


class TagConcept(models.Model):
    """
    class to tag the objects by concept. The search is handled by graphsearch
    """
    label = models.CharField(max_length=100)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    def __str__(self):
        return self.label


class TagProblemType(models.Model):
    """
    class to tag the resources by problem type, for example 'problème de la balle de ping pong'
    """
    label = models.CharField(max_length=150)

    def __str__(self):
        return self.label


class TagProblemTypeResource(models.Model):
    """
    link between problem type and resources. 1 resource can have
    multiple problemtype and viceversa
    """
    tag_problem_type = models.ForeignKey(TagProblemType, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)


class TagLevelResource(models.Model):
    """
    assign a level to a resource
    """
    tag_level = models.ForeignKey(TagLevel, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag_level.label
