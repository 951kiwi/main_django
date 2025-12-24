from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Question, Player, Answer, QuizState,Link,Data


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "time_limit", "correct")
    list_editable = ("time_limit",)
    search_fields = ("text",)


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ("id", "surprise")

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "photo_preview")
    readonly_fields = ("photo_preview",)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:100px; border-radius:8px;" />',
                obj.photo.url
            )
        return "画像なし"

    photo_preview.short_description = "プレビュー"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("player", "question", "choice")
    list_filter = ("question",)


@admin.register(QuizState)
class QuizStateAdmin(admin.ModelAdmin):
    list_display = ("id", "current_question", "is_accepting", "started_at")
    actions = ["start_quiz", "stop_quiz", "reset_timer"]

    def start_quiz(self, request, queryset):
        for state in queryset:
            state.is_accepting = True
            state.started_at = timezone.now()
            state.save()
    start_quiz.short_description = "▶ 回答受付を開始"

    def stop_quiz(self, request, queryset):
        queryset.update(is_accepting=False)
    stop_quiz.short_description = "■ 回答受付を停止"

    def reset_timer(self, request, queryset):
        for state in queryset:
            state.started_at = timezone.now()
            state.save()
    reset_timer.short_description = "⏱ タイマーをリセット"

class Linkadmin(admin.ModelAdmin):
    list_display = ("title","rank")  # 一覧表示
    list_editable = ('rank',)  # 直接編集可能
    list_display_links = ('title',)  # タイトルはリンクとして保持
    ordering = ('rank',)  # ここで rank 順にソート
admin.site.register(Link,Linkadmin)