from django.contrib import admin
from django.utils import timezone
from .models import Question, Player, Answer, QuizState


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "time_limit", "correct")
    list_editable = ("time_limit",)
    search_fields = ("text",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


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
