import os

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
import random
import string
# Create your models here.


FR = "FRANÇAIS"
EN = "ENGLISH"

LANGUAGES_CHOICES = (
        (FR, "Français"),
        #(IT, "Italiano"),
        (EN, "English"),
    )


class Kernel(models.Model):
    name = models.CharField(max_length=255)


def git_repository_directory_path(instance, filename):
    return "notebooks/{}/{}".format(instance.git_repository.slug, filename)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, max_length)


class GitRepository(models.Model):
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=8, choices=LANGUAGES_CHOICES, default=FR)
    course = models.CharField(max_length=255)
    kernel = models.ManyToManyField(Kernel, related_name="kernel", blank=True)
    teacher = models.CharField(max_length=255)
    repository = models.URLField(max_length=255)
    short_description = models.CharField(max_length=500, blank=True)
    long_description = models.CharField(max_length=1500, blank=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    local_path = models.FilePathField(path='/home/maria/Documents/epfl/notebooks/notebooks_test')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        slugs_list = GitRepository.objects.values_list('slug', flat=True)
        suffix_slug = ''
        if self.slug in slugs_list:
            suffix_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.slug += suffix_slug
        super(GitRepository, self).save(*args, **kwargs)

    def get_teacher_name(self):
        return self.teacher

    def get_course_name(self):
        return self.course

    def get_kernels_names(self):
        kernel_list = ''
        for kernel in self.kernel.all():
            kernel_list += kernel.name + ' '
        return kernel_list

    def get_ipynb_rel_path(self):
        dict_path = []
        for dir_, _, files in os.walk(self.local_path):
            for file_name in files:
                dict = {}
                if file_name.endswith('.ipynb'):
                    local_path = os.path.join(os.path.relpath(dir_, self.local_path),file_name).split('/')
                    dict['name'] = local_path[0]
                    dict['children'] = []
                    if len(local_path) == 2:
                        dict['children'].append({'name': local_path[1], 'children': []})
                    if len(local_path) > 2:
                        for i in range(1, len(local_path)-1):
                            dict['children'].append({'name': local_path[i],
                                                     'children': [{'name': local_path[i+1]}]})
                    dict_path.append(dict)
        return dict_path


class Notebook(models.Model):
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=8, choices=LANGUAGES_CHOICES, default=FR)
    git_repository = models.ForeignKey(GitRepository, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=500, blank=True)
    long_description = models.CharField(max_length=1500, blank=True)
    type = models.CharField(max_length=255)
    html_view = models.FileField(upload_to=git_repository_directory_path, storage=OverwriteStorage, blank=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        slugs_list = Notebook.objects.values_list('slug', flat=True)
        suffix_slug = ''
        if self.slug in slugs_list:
            suffix_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.slug += suffix_slug
        super(Notebook, self).save(*args, **kwargs)
