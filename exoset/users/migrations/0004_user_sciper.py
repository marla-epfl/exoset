# Generated by Django 3.0.4 on 2021-05-03 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_user_sciper'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sciper',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
