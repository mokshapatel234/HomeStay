# Generated by Django 3.2.8 on 2023-07-25 10:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0002_auto_20230717_1145'),
        ('userapi', '0002_rename_status_bookproperty_book_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=4)),
                ('is_verified', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_otp', to='superadmin.customer')),
            ],
        ),
    ]
