from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

# Keep file uploads in the same media tree used by the rest of the project.
FILEUPLOAD_ROOT = Path(settings.MEDIA_ROOT) / "fileuploads"
fileupload_storage = FileSystemStorage(location=str(FILEUPLOAD_ROOT))

class UploadedFile(models.Model):
    """Legacy model retained for migration compatibility."""
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class DocumentFile(models.Model):
    original_name = models.CharField("ファイル名", max_length=255)
    relative_path = models.CharField("相対パス", max_length=1024, db_index=True)
    file = models.FileField("保存ファイル", storage=fileupload_storage, upload_to="documents/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="managed_documents", verbose_name="アップロードユーザー")
    uploaded_at = models.DateTimeField("アップロード日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    class Meta:
        ordering = ("relative_path",)
        constraints = [models.UniqueConstraint(fields=("uploaded_by", "relative_path"), name="fileuploader_user_relative_path_uniq")]
    @property
    def extension(self):
        return Path(self.original_name).suffix.lower()
    @property
    def is_image(self):
        return self.extension in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    @property
    def is_pdf(self):
        return self.extension == ".pdf"
    @property
    def is_office_document(self):
        return self.extension in {".docx", ".xlsx", ".pptx"}
    def __str__(self):
        return self.relative_path
