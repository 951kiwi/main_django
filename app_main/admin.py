from django.contrib import admin
from .models import Link


class Linkadmin(admin.ModelAdmin):
    list_display = ("title","rank")  # 一覧表示
    list_editable = ('rank',)  # 直接編集可能
    list_display_links = ('title',)  # タイトルはリンクとして保持
    ordering = ('rank',)  # ここで rank 順にソート

admin.site.register(Link,Linkadmin)