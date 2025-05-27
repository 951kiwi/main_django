# admin.py
from django.contrib import admin
from .models import Selection,Video,Line

class SelectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'login','game01','game02','game03','game04','game05','game06')  # 表示するフィールドを指定

# モデルを管理画面に登録
admin.site.register(Selection, SelectionAdmin)
admin.site.register(Video)
admin.site.register(Line)