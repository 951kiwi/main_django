from django.db import models
from datetime import timedelta, date
from django.db.models.signals import pre_delete , pre_save
import os
from django.dispatch import receiver


class MonthlyRecord(models.Model):
    month = models.DateField(unique=True)  # 各月の記録
    fuel_efficiency = models.FloatField(default=8)  # リッターあたりの燃費（km/L）
    cost_per_liter = models.IntegerField(default=170)  # リッターあたりのガソリン代（円）
    is_check = models.BooleanField(default=False) #チェックが完了したか
    is_payed = models.BooleanField(default=False) #支払済か
    def __str__(self):
        return self.month.strftime("%Y-%m")
    

class GasRecord(models.Model):
    date = models.DateField()
    distance = models.FloatField()  # 走行距離（km）
    image = models.ImageField(upload_to='FamilyCar/gasData' ,null=True,blank=True)
    monthly_record = models.ForeignKey(MonthlyRecord, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.distance}km"
    
    def save(self, *args, **kwargs):
        # `MonthlyRecord` の month を計算
        month_start = self.date.replace(day=1)
        # `MonthlyRecord` を取得または作成
        monthly_record, created = MonthlyRecord.objects.get_or_create(month=month_start)
         # 2024年8月以降で足りない月の `MonthlyRecord` を作成
        self.create_missing_monthly_records(month_start)
        # 変更前の `MonthlyRecord` から削除（必要なら）
        if self.pk:  # 既存のデータがある場合のみ
            old_instance = GasRecord.objects.get(pk=self.pk)
        # 新しい `MonthlyRecord` を設定
        self.monthly_record = monthly_record
        super().save(*args, **kwargs)  # 通常の保存

    def create_missing_monthly_records(self, start_date):
        # 2024年8月から作成する
        start_month = start_date.replace(day=1)
        reference_date = date(2024, 8, 1)
        # 2024年8月以降で足りない月を確認して作成
        if start_month >= reference_date:
            current_month = reference_date
            last_month = start_month - timedelta(days=1)
            # 現在の月から過去の月を作成
            while current_month <= last_month:
                if not MonthlyRecord.objects.filter(month=current_month).exists():
                    MonthlyRecord.objects.create(month=current_month)
                current_month += timedelta(days=32)
                current_month = current_month.replace(day=1)  # 月初に戻す

@receiver(pre_delete, sender=GasRecord)
def image_card_pre_delete(sender, instance, **kwargs):
    # インスタンスに関連する画像を削除
    if instance.image and instance.image.name:
        if os.path.isfile(instance.image.path):  # ファイルが存在する場合
            os.remove(instance.image.path)  # 画像を削除

@receiver(pre_save, sender=GasRecord)
def delete_old_image(sender, instance, **kwargs):
    """GasRecordの画像が変更された場合、古い画像を削除"""
    if instance.pk:  # 既存のデータがある場合のみ
        old_instance = GasRecord.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image != instance.image:  # 画像が変更された
            if os.path.isfile(old_instance.image.path):
                os.remove(old_instance.image.path)  # 古い画像を削除