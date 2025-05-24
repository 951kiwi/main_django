from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import Link, UserActivityLog


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'method', 'path_short', 'ip_address', 'short_user_agent')
    list_filter = ('method', 'timestamp', 'user')  # ← user をフィルターに追加
    search_fields = ('user__username', 'path', 'ip_address', 'user_agent')
    list_select_related = ('user',)  # パフォーマンス向上
    list_display_links = ('timestamp', 'user')  # ← ユーザー名クリックで詳細へ
    readonly_fields = [f.name for f in UserActivityLog._meta.fields]
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'

    def path_short(self, obj):
        return (obj.path[:50] + '...') if len(obj.path) > 50 else obj.path
    path_short.short_description = 'Path'

    def short_user_agent(self, obj):
        return (obj.user_agent[:40] + '...') if len(obj.user_agent) > 40 else obj.user_agent
    short_user_agent.short_description = 'User Agent'


class Linkadmin(admin.ModelAdmin):
    list_display = ("title","rank")  # 一覧表示
    list_editable = ('rank',)  # 直接編集可能
    list_display_links = ('title',)  # タイトルはリンクとして保持
    ordering = ('rank',)  # ここで rank 順にソート


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("id","username","is_staff","last_login","last_activity")
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ("last_activity",'profile_image', 'nickname')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ("last_activity",'profile_image', 'nickname')}),
    )

admin.site.register(Link,Linkadmin)
admin.site.register(CustomUser, CustomUserAdmin)