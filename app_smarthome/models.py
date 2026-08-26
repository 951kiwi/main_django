from django.db import models


class Device(models.Model):

    TYPE_CHOICES = [
        ("hub","ハブ"),
        ("light", "ライト"),
        ("light_detail","ライト詳細付き"),
        ("concent","コンセント"),
        ("tv", "テレビ"),
        ("aircon", "エアコン"),
        ("PC","パソコン"),
        ("remote", "リモコン"),
    ]

    name = models.CharField(max_length=100)

    device_id = models.CharField(
        max_length=100,
        unique=True
    )

    device_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )
    # 複数機能のキー一覧を配列で保持
    FEATURE_CHOICES = [
        ("power_check","電源チェック"),
        ("brightness_step", "ライト：明るさ調整"),
        ("brightness_slider", "ライト：明るさ調整（詳細）"),
        ("temperate_step", "ライト：調色（冷暖）"),
        ("temperate_slider", "ライト：調色（冷暖）（詳細）"),
        ("color_slider", "ライト：色変更（詳細）"),
        ("scene", "ライト：シーン切り替え"),
        ("night_light", "ライト：常夜灯"),
        ("timer_30", "ライト：30分切タイマー"),
    ]
    # ↓↓↓ この行が必要です ↓↓↓
    features = models.JSONField(default=list, blank=True, verbose_name="対応機能")

    def __str__(self):
        return self.name
    
class Command(models.Model):

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="commands"
    )

    name = models.CharField(
        max_length=100
    )
    TYPE_CHOICES = [
            ("command", "command"),
            ("customize", "customize"),
        ]
    command_type = models.CharField(
            max_length=20,
            choices=TYPE_CHOICES
        )

    command = models.CharField(
        max_length=100
    )
    parameter = models.CharField(
        max_length=500,
        default="default"
    )


    def __str__(self):
        return f"{self.device.name} - {self.name}"

class Card(models.Model):

    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="card"
    )
    title = models.CharField(
        max_length=100
    )
    sub_title = models.CharField(
            max_length=100
        )

    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

    width = models.IntegerField(default=4)
    height = models.IntegerField(default=4)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.device.name} Card"
    
class OperationLog(models.Model):
    # どのデバイスに対する操作か（デバイス削除時もログを残すため SET_NULL）
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
        verbose_name="デバイス"
    )
    
    # 実行した操作内容（例: '電源ON', '温度変更: 25°C', 'シャットダウン'）
    action = models.CharField(max_length=200, verbose_name="操作内容")
    
    # 送信したコマンドや追加データ（任意・JSON形式）
    details = models.JSONField(default=dict, blank=True, verbose_name="詳細データ")
    
    # 実行日時（新しい順で並び替え）
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作日時")

    class Meta:
        verbose_name = "操作履歴"
        verbose_name_plural = "操作履歴"
        ordering = ["-created_at"]

    def __str__(self):
        device_name = self.device.name if self.device else "不明なデバイス"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {device_name} - {self.action}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # 保存後に100件を超える古いログを削除
        MAX_LOG_COUNT = 100
        
        # 100件以降の古いレコードのIDリストを取得
        old_ids = OperationLog.objects.order_by("-created_at").values_list("id", flat=True)[MAX_LOG_COUNT:]
        
        if old_ids:
            OperationLog.objects.filter(id__in=list(old_ids)).delete()