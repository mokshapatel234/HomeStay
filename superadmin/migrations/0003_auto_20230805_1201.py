# Generated by Django 3.2.8 on 2023-08-05 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0002_auto_20230717_1145'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.AddField(
            model_name='properties',
            name='is_favourite',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customer',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
