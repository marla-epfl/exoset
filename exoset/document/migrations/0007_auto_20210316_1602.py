# Generated by Django 3.0.4 on 2021-03-16 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_auto_20210316_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcesourcefile',
            name='source',
            field=models.FilePathField(path='/home/maria/Documents/epfl/exoset_project/exoset/exoset/exoset/media/github'),
        ),
        migrations.AlterField(
            model_name='resourcesourcefile',
            name='style',
            field=models.FilePathField(blank=True, null=True, path='/home/maria/Documents/epfl/exoset_project/exoset/exoset/exoset/media/github'),
        ),
    ]
