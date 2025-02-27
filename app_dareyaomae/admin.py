from django.contrib import admin
from .models import Room,Player,Image_Card,Select_Card

# Register your models here.

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0 # 初期表示で何行分の入力フォームを表示するか

class Image_CardInline(admin.TabularInline):
    model = Image_Card
    extra = 0

class SelectCardInline(admin.TabularInline):
    model = Select_Card
    extra = 0 # 初期表示で何行分の入力フォームを表示するか

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'password','id','created_at')  # 'name'と'id'を表示
    inlines = [PlayerInline,Image_CardInline,SelectCardInline]
    readonly_fields = ('created_at',)  # 追加
    



class PlayerAdmin(admin.ModelAdmin):
    list_display = ( 'name','room','id','created_at')  # 'name'と'id'を表示
    inlines = [Image_CardInline]


class Image_CardAdmin(admin.ModelAdmin):
    list_display = ('room' ,'player' ,'image','id','created_at')  # 'name'と'id'を表示

class Select_CardAdmin(admin.ModelAdmin):
    list_display = ('image_card','is_drawn','get_player','id')  # 'name'と'id'を表示




admin.site.register(Room,RoomAdmin)
admin.site.register(Player,PlayerAdmin)
admin.site.register(Image_Card,Image_CardAdmin)
admin.site.register(Select_Card)