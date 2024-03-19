from django.db import models
from django.utils.translation import gettext_lazy as _
from exoset.document.models import Resource

# Create your models here.


class Prerequisite(models.Model):
    """
    this class defines the prerequisites to solve an exercise
    """
    MAT = 'MAT'
    PHY = 'PHY'
    CHE = 'CHE'

    DOMAIN_CHOICES = (
        (MAT, _('Mathematics')),
        (PHY,  _('Physics')),
        (CHE, _('Chemistry')),
    )
    domain = models.CharField(max_length=3, choices=DOMAIN_CHOICES, default=MAT)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.domain + ":" + self.label


class AssignPrerequisiteResource(models.Model):
    """
    link between resource and prerequisites
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    prerequisite = models.ManyToManyField(Prerequisite)
