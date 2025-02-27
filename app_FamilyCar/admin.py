from django.contrib import admin
from django.utils.timezone import now
from .models import GasRecord,MonthlyRecord
# Register your models here.

class GasInline(admin.TabularInline):
    model = GasRecord
    extra = 0

class MonthlyAdmin(admin.ModelAdmin):
    inlines = [GasInline]
    list_display = ('formatted_month', 'gas_record_count') 

    def gas_record_count(self, obj):
        """関連する GasRecord の数を返す"""
        return obj.gasrecord_set.count()  # gasrecord_set は ForeignKey の逆参照
    gas_record_count.short_description = 'ガスデータ数'  # カスタム列のタイトル
    def formatted_month(self, obj):
        """月を 'YYYY年M月' の形式で表示する"""
        return obj.month.strftime('%Y年%m月')

    formatted_month.short_description = '月'  # 列タイトルを '月' に設定
    
admin.site.register(GasRecord)
admin.site.register(MonthlyRecord,MonthlyAdmin)