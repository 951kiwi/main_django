import os
from django.db.models.signals import pre_save, post_delete
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
# Create your models here.




class Selection(models.Model):
    login = models.BooleanField(default=False)
    name = models.CharField(max_length=20 ,null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gamestart = models.BooleanField(default=False) 
    game01 = models.BooleanField(default=False)
    game02 = models.BooleanField(default=False)
    game03 = models.BooleanField(default=False)
    game04 = models.BooleanField(default=False)
    game05 = models.BooleanField(default=False)
    game06 = models.BooleanField(default=False)

class Line(models.Model):
    he_name = models.CharField(max_length=255)
    he_image = models.ImageField(upload_to='lover/line/image')
    she_name = models.CharField(max_length=255)
    she_image = models.ImageField(upload_to='lover/line/image')
    backgroundImage = models.ImageField(upload_to='lover/line/image' , null=True , blank=True)
    

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    



# ===== シグナル処理 =====


@receiver(pre_save, sender=Line)
def auto_delete_old_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # 新規作成時はスキップ

    try:
        old_file = sender.objects.get(pk=instance.pk).he_image
    except sender.DoesNotExist:
        return

    new_file = instance.he_image
    if not old_file == new_file and old_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

@receiver(post_delete, sender=Line)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.he_image and os.path.isfile(instance.he_image.path):
        os.remove(instance.he_image.path)