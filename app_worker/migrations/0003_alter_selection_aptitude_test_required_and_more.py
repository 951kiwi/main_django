# Generated by Django 5.1 on 2025-02-26 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_worker', '0002_alter_selection_interview_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selection',
            name='aptitude_test_required',
            field=models.BooleanField(default=False, verbose_name='適性検査あり'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='aptitude_test_taken',
            field=models.BooleanField(default=False, verbose_name='適性検査'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='company_name',
            field=models.CharField(max_length=255, verbose_name='企業名'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='interview_status',
            field=models.CharField(choices=[('none', 'なし'), ('briefing', '説明会済'), ('interview_1', '1次面接'), ('interview_2', '2次面接'), ('interview_3', '3次面接'), ('interview_4', '4次面接'), ('interview_5', '5次面接'), ('final', '最終面接'), ('offer', '内定'), ('rejected', '落ちた')], default='none', max_length=20, verbose_name='選考状況'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='memo',
            field=models.TextField(blank=True, null=True, verbose_name='メモ'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='resume_required',
            field=models.BooleanField(default=False, verbose_name='履歴書あり'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='resume_submitted',
            field=models.BooleanField(default=False, verbose_name='履歴書'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='web_test_required',
            field=models.BooleanField(default=False, verbose_name='webテストあり'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='web_test_taken',
            field=models.BooleanField(default=False, verbose_name='webテスト'),
        ),
    ]
