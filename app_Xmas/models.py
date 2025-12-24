import os
from django.db import models

# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ImageField(
        upload_to="xmas/players/",
        blank=True,
        null=True
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
    # 既存データがある場合
        if self.pk:
            try:
                old = Player.objects.get(pk=self.pk)
                if old.photo and old.photo != self.photo:
                    if os.path.isfile(old.photo.path):
                        os.remove(old.photo.path)
            except Player.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.photo and os.path.isfile(self.photo.path):
            os.remove(self.photo.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

class Data(models.Model):
    surprise = models.BooleanField()

class Question(models.Model):
    text = models.TextField()
    choice_a = models.CharField(max_length=100)
    choice_b = models.CharField(max_length=100)
    choice_c = models.CharField(max_length=100)
    choice_d = models.CharField(max_length=100)
    correct = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )

    time_limit = models.PositiveIntegerField(default=10)  # ← 秒数
    def __str__(self):
        return self.text[:20]


class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=1)
    answered_at = models.DateTimeField(auto_now_add=True)

# app_Xmas/models.py

class QuizState(models.Model):
    current_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_accepting = models.BooleanField(default=False)  # 回答受付中か
    started_at = models.DateTimeField(null=True, blank=True)  # ← これ
    show_answer = models.BooleanField(default=False)  # ← 正解表示中か

# Create your models here.
class Link(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    image = models.ImageField(upload_to='xmas/links/', blank=True, null=True ,default='links/dafault.jpg')
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    