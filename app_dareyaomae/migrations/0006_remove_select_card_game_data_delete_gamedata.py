# Generated by Django 4.1 on 2024-01-23 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_dareyaomae', '0005_remove_gamedata_image_card_select_card_game_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='select_card',
            name='game_data',
        ),
        migrations.DeleteModel(
            name='GameData',
        ),
    ]
