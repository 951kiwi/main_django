from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    profile_image = models.ImageField("プロフィール画像",upload_to='profile_images/', blank=True, null=True)
    nickname = models.CharField("ニックネーム",max_length=20, blank=True, null=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    

class UserActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    path = models.CharField(max_length=512)
    method = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'ログ'              # 単数形表示名（例：UserActivityLog オブジェクト → ログ）
        verbose_name_plural = 'アクティビティログ'  # 一覧表示名（例：User activity logs → ユーザーアクティビティログ一覧）

    def __str__(self):
        return f"[{self.timestamp}] {self.user} {self.method} {self.path}"

# Create your models here.
class Link(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    image = models.ImageField(upload_to='links/', blank=True, null=True ,default='links/dafault.jpg')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL , related_name='links', blank=True)  # 複数のユーザーと関連付け
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
