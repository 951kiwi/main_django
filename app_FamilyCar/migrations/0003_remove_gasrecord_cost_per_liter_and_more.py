# Generated by Django 5.1 on 2025-02-08 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_FamilyCar', '0002_gasrecord_monthlyrecord_delete_driverecord'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gasrecord',
            name='cost_per_liter',
        ),
        migrations.RemoveField(
            model_name='gasrecord',
            name='fuel_amount',
        ),
        migrations.RemoveField(
            model_name='gasrecord',
            name='time',
        ),
    ]
