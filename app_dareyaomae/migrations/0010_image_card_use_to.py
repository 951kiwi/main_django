# Generated by Django 4.1 on 2024-01-24 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_dareyaomae', '0009_image_card_card_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='image_card',
            name='use_to',
            field=models.BooleanField(default=False),
        ),
    ]
