from django.db import models

# Create your models here.


class GitHubRepository(models.Model):
    repository_name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    official = models.BooleanField(default=False)


