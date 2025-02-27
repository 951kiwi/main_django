from django.db import models
from django.utils import timezone

# Create your models here.
class PlayerData(models.Model):
    player_name = models.CharField(max_length=100)  # プレイヤー名
    join_time = models.DateTimeField()  # 参加時間
    leave_time = models.DateTimeField(null=True, blank=True)  # 退場時間（NULL可）
    current_world = models.CharField(max_length=100,null=True, blank=True)  # 現在の世界
    last_death_world = models.CharField(max_length=100,null=True, blank=True)  # 最後に死んだ世界
    last_death_x = models.IntegerField(null=True, blank=True)  # 最後に死んだ座標x
    last_death_y = models.IntegerField(null=True, blank=True)  # 最後に死んだ座標y
    last_death_z = models.IntegerField(null=True, blank=True)  # 最後に死んだ座標z
    total_play_time = models.DurationField(default=timezone.timedelta)  # 累積プレイ時間
    def update_play_time(self):
        """ オフライン時にプレイ時間を計算して保存 """
        if self.leave_time and self.leave_time > self.join_time:
            play_time = self.leave_time - self.join_time
            self.total_play_time += play_time
            self.save()
            
    image = models.ImageField(upload_to='player_images/', default='player_images/default_image.png')  # 画像

    def __str__(self):
        return self.player_name