# Generated by Django 5.1 on 2025-02-03 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_dareyaomae', '0014_alter_select_card_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image_card',
            name='image',
            field=models.ImageField(upload_to='dareyaomae/upload/'),
        ),
    ]
