from django.contrib import admin
from .models import UploadedFile
# Register your models here.


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')

admin.site.register(UploadedFile, UploadedFileAdmin)