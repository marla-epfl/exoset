# Generated by Django 3.0.4 on 2021-04-26 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210426_0917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='sciper',
        ),
    ]
