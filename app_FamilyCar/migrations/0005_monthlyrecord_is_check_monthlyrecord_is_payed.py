# Generated by Django 5.1 on 2025-02-10 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_FamilyCar', '0004_remove_monthlyrecord_gas_records_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyrecord',
            name='is_check',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monthlyrecord',
            name='is_payed',
            field=models.BooleanField(default=False),
        ),
    ]
