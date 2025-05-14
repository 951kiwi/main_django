from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import Link


class Linkadmin(admin.ModelAdmin):
    list_display = ("title","rank")  # 一覧表示
    list_editable = ('rank',)  # 直接編集可能
    list_display_links = ('title',)  # タイトルはリンクとして保持
    ordering = ('rank',)  # ここで rank 順にソート


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("id","username","is_staff","last_login")
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('profile_image', 'nickname')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('profile_image', 'nickname')}),
    )

admin.site.register(Link,Linkadmin)
admin.site.register(CustomUser, CustomUserAdmin)