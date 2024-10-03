import os

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
import random
import string
from django.utils.translation import gettext_lazy as _
# Create your models here.


FR = "Français"
EN = "English"

LANGUAGES_CHOICES = (
        (FR, "Français"),
        (EN, "English"),
    )


class NBType(models.Model):
    name = models.CharField(max_length=100)


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
    local_path = models.FilePathField(path=settings.MEDIA_ROOT + "/notebooks/", allow_files=False, allow_folders=True,
                                      max_length=255)
    last_commit = models.CharField(max_length=255, blank=True, null=True)

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


class Notebook(models.Model):
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=8, choices=LANGUAGES_CHOICES, default=FR)
    git_repository = models.ForeignKey(GitRepository, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=500, blank=True)
    long_description = models.CharField(max_length=1500, blank=True)
    nb_type = models.ForeignKey(NBType, on_delete=models.CASCADE, blank=True, null=True)
    html_view = models.FileField(upload_to=git_repository_directory_path, storage=OverwriteStorage, blank=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        slugs_list = Notebook.objects.values_list('slug', flat=True)
        suffix_slug = ''
        if self.slug in slugs_list:
            suffix_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.slug += suffix_slug
        super(Notebook, self).save(*args, **kwargs)

    def get_ipynb_rel_path(self):
        list_path = []
        for dir_, _, files in os.walk(self.git_repository.local_path):
            for file_name in files:
                if file_name.endswith('.ipynb'):
                    local_path = os.path.join(os.path.relpath(dir_, self.git_repository.local_path), file_name).split('/')
                    current_list_path = list_path
                    for part_local_path in local_path:
                        new_path_part_dict = {'name': part_local_path, 'children': []}
                        current_path_dict = None
                        for idx_path, path in enumerate(current_list_path):
                            if path['name'] == part_local_path:
                                current_path_dict = path
                                break
                        if current_path_dict:
                            current_list_path = current_path_dict['children']
                        else:
                            current_list_path.append(new_path_part_dict)
                            current_list_path = new_path_part_dict['children']
        return sorted(list_path, key=lambda d: d['name'])

    def get_notebook_rel_path(self):
        list_path = []
        git_repository = self.git_repository
        all_notebooks = Notebook.objects.filter(git_repository=git_repository)
        for file in all_notebooks:
            local_path = file.file_path.split('/')
            current_list_path = list_path
            for part_local_path in local_path:
                new_path_part_dict = {'slug': file.slug, 'name': part_local_path, 'children': []}
                current_path_dict = None
                for idx_path, path in enumerate(current_list_path):
                    if path['name'] == part_local_path:
                        current_path_dict = path
                        break
                if current_path_dict:
                    current_list_path = current_path_dict['children']
                else:
                    current_list_path.append(new_path_part_dict)
                    current_list_path = new_path_part_dict['children']
        print(sorted(list_path, key=lambda d: d['name']))
        return sorted(list_path, key=lambda d: d['name'])
