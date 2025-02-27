from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Link(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    image = models.ImageField(upload_to='links/', blank=True, null=True ,default='links/dafault.jpg')
    users = models.ManyToManyField(User, related_name='links', blank=True)  # 複数のユーザーと関連付け
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    