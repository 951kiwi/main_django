import uuid
from django.db import models

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, default="対戦部屋")
    board_size = models.IntegerField(default=9)
    fences_per_player = models.IntegerField(default=10)

    current_turn = models.IntegerField(default=1)  # 1: 下側 (Player 1), 2: 上側 (Player 2)
    winner = models.IntegerField(null=True, blank=True)

    p1_pos = models.JSONField(default=dict)
    p2_pos = models.JSONField(default=dict)
    p1_fences_left = models.IntegerField(default=10)
    p2_fences_left = models.IntegerField(default=10)

    placed_fences = models.JSONField(default=list)  # [{"x": int, "y": int, "orientation": "H"|"V"}]

    def save(self, *args, **kwargs):
        if not self.p1_pos:
            mid = self.board_size // 2
            self.p1_pos = {"x": mid, "y": self.board_size - 1}
            self.p2_pos = {"x": mid, "y": 0}
            self.p1_fences_left = self.fences_per_player
            self.p2_fences_left = self.fences_per_player
        super().save(*args, **kwargs)