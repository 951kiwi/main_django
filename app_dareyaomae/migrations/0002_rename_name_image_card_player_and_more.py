# Generated by Django 4.1 on 2024-01-23 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_dareyaomae', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image_card',
            old_name='name',
            new_name='player',
        ),
        migrations.RemoveField(
            model_name='image_card',
            name='is_drawn',
        ),
    ]
