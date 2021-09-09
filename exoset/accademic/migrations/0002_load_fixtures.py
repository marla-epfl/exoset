# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-29 08:25
from __future__ import unicode_literals

from django.db import migrations


def load_stores_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "accademic")
    call_command("loaddata", "courses")


class Migration(migrations.Migration):

    dependencies = [
        ('accademic', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_stores_from_fixture),
    ]
