# Generated for the browser-based private file manager.
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import migrations, models
import django.db.models.deletion
from pathlib import Path


def fileupload_storage():
    return FileSystemStorage(location=str(Path(settings.MEDIA_ROOT) / "fileuploads"))


class Migration(migrations.Migration):
    dependencies = [
        ("app_fileuploader", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("original_name", models.CharField(max_length=255, verbose_name="ファイル名")),
                ("relative_path", models.CharField(db_index=True, help_text="アップロード時のフォルダ構造を保持します。", max_length=1024, verbose_name="相対パス")),
                ("file", models.FileField(storage=fileupload_storage(), upload_to="documents/", verbose_name="保存ファイル")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, verbose_name="アップロード日時")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新日時")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="managed_documents", to=settings.AUTH_USER_MODEL, verbose_name="アップロードユーザー")),
            ],
            options={"ordering": ("relative_path",)},
        ),
        migrations.AddConstraint(
            model_name="documentfile",
            constraint=models.UniqueConstraint(fields=("uploaded_by", "relative_path"), name="fileuploader_user_relative_path_uniq"),
        ),
    ]
