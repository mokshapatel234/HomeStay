# Generated by Django 3.2.8 on 2023-06-23 05:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('superadmin', '0003_propertyterms'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdminUser',
            new_name='TermsandPolicy',
        ),
    ]
