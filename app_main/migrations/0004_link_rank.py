# Generated by Django 5.1 on 2025-02-08 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_main', '0003_remove_link_user_link_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='rank',
            field=models.IntegerField(default=0),
        ),
    ]
