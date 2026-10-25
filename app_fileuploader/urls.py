from django.urls import path
from . import views

app_name = "fileuploader"
urlpatterns = [
    path("", views.file_manager, name="manager"),
    path("upload/", views.upload_files, name="upload"),
    path("file/<int:file_id>/content/", views.file_content, name="file_content"),
    path("file/<int:file_id>/download/", views.download_file, name="download"),
    path("file/<int:file_id>/delete/", views.delete_file, name="delete"),
    path("file/<int:file_id>/edit/", views.office_editor, name="office_editor"),
    path("file/<int:file_id>/onlyoffice-callback/", views.onlyoffice_callback, name="onlyoffice_callback"),
    path("upload_success/", views.file_manager, name="upload_success"),
]
