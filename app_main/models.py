from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    profile_image = models.ImageField("プロフィール画像",upload_to='profile_images/', blank=True, null=True)
    nickname = models.CharField("ニックネーム",max_length=20, blank=True, null=True)
    
# Create your models here.
class Link(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    image = models.ImageField(upload_to='links/', blank=True, null=True ,default='links/dafault.jpg')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL , related_name='links', blank=True)  # 複数のユーザーと関連付け
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
