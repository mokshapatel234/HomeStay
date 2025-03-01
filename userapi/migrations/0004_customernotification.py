# Generated by Django 3.2.8 on 2023-08-05 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0003_auto_20230805_1201'),
        ('userapi', '0003_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.CharField(max_length=255)),
                ('viewed', models.BooleanField(default=False)),
                ('send_by', models.CharField(default=False, max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_notification', to='superadmin.customer')),
            ],
        ),
    ]
