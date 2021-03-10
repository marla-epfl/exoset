from django.db import models
from exoset.document.models import Resource
# Create your models here.


class Sector(models.Model):
    """
    identify a category of disciplinary field (biology, engineering, science of life..)
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)


class Course(models.Model):
    """
    class for storing all information about a class
    """
    EPFL = "EPFL"
    INSTITUTE_CHOICES = (
        (EPFL, 'EPFL'),
    )
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    SEMESTER_CHOICES = (
        (I, 'I'),
        (II, 'II'),
        (III, 'III'),
        (IV, 'IV'),
    )
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    institute = models.CharField(max_length=4, choices=INSTITUTE_CHOICES, default=EPFL)
    semester = models.CharField(max_length=4, choices=SEMESTER_CHOICES, default=I)
    resource = models.ManyToManyField(Resource, blank=True)

    def __str__(self):
        return self.sector.name + self.semester

