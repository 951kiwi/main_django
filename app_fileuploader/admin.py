from django.contrib import admin
from .models import DocumentFile, UploadedFile

@admin.register(DocumentFile)
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ("relative_path", "uploaded_by", "uploaded_at", "updated_at")
    list_filter = ("uploaded_at", "updated_at")
    search_fields = ("relative_path", "original_name", "uploaded_by__username")
    readonly_fields = ("uploaded_at", "updated_at")

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
