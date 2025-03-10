from django.db import models
from django.utils import timezone
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


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title