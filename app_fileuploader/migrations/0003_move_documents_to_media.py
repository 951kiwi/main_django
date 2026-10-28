"""Copy files from the old private_documents directory into MEDIA_ROOT/fileuploads.

Safe to run on fresh installs (where there are no DocumentFile rows) and on
installations that already applied the earlier private-storage migration.
"""
from pathlib import Path
import shutil

from django.conf import settings
from django.db import migrations


def copy_existing_documents(apps, schema_editor):
    DocumentFile = apps.get_model("app_fileuploader", "DocumentFile")
    old_root = Path(settings.BASE_DIR) / "private_documents"
    new_root = Path(settings.MEDIA_ROOT) / "fileuploads"
    if not old_root.exists():
        return
    for item in DocumentFile.objects.all().iterator():
        relative_name = item.file.name
        if not relative_name:
            continue
        source = old_root / relative_name
        destination = new_root / relative_name
        if source.is_file() and not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


class Migration(migrations.Migration):
    dependencies = [
        ("app_fileuploader", "0002_documentfile"),
    ]

    operations = [
        migrations.RunPython(copy_existing_documents, migrations.RunPython.noop),
    ]
