from django.contrib import admin
from django import forms
from django.utils.timezone import now
from .models import PlayerData
# Register your models here.
admin.site.site_header = "カスタム管理画面"

class PlayerDataAdmin(admin.ModelAdmin):
    list_display = ("player_name", "join_time", "leave_time",'total_play_time' ,"status_duration", "is_online")  # 一覧表示
    # オンライン・オフライン判定
    def is_online(self, obj):
        if obj.leave_time is None or obj.leave_time < obj.join_time:
            return "🟢 Online"
        return "🔴 Offline"
    # 状態の継続時間を計算
    def status_duration(self, obj):
        if obj.leave_time is None or obj.leave_time < obj.join_time:
            duration = now() - obj.join_time  # 現在時刻 - 参加時間
        else:
            duration = now() - obj.leave_time# 退出時間 - 参加時間

        # hh:mm:ss にフォーマット
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    status_duration.short_description = "継続時間"
            
    is_online.short_description = "ステータス"  # カラム名を変更

admin.site.register(PlayerData,PlayerDataAdmin)