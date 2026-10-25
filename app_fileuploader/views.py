import json
import os
import secrets
from pathlib import PurePosixPath

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import DocumentFile

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".docx", ".xlsx", ".pptx", ".txt", ".csv", ".md", ".zip", ".7z", ".rar", ".mp4", ".mp3"}
MAX_UPLOAD_BYTES = int(getattr(settings, "FILEUPLOADER_MAX_UPLOAD_BYTES", 100 * 1024 * 1024))

def _safe_relative_path(raw_path, fallback_name):
    raw_path = (raw_path or fallback_name or "").replace("\\", "/")
    path = PurePosixPath(raw_path)
    parts = [part for part in path.parts if part not in ("", ".", "/")]
    if not parts or any(part == ".." for part in parts):
        raise ValueError("不正なファイルパスです。")
    if ":" in parts[0] or any(ord(ch) < 32 for part in parts for ch in part):
        raise ValueError("不正なファイルパスです。")
    normalized = "/".join(parts)
    if len(normalized) > 1024:
        raise ValueError("ファイルパスが長すぎます。")
    return normalized

def _owned_file(request, file_id):
    return get_object_or_404(DocumentFile, pk=file_id, uploaded_by=request.user)

@login_required
def file_manager(request):
    files = DocumentFile.objects.filter(uploaded_by=request.user)
    folder = request.GET.get("folder", "").strip("/")
    if folder:
        files = files.filter(relative_path__startswith=folder + "/")
    return render(request, "fileuploader/manager.html", {
        "files": files, "current_folder": folder,
        "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
        "onlyoffice_enabled": bool(getattr(settings, "ONLYOFFICE_DOCUMENT_SERVER_URL", "") and getattr(settings, "ONLYOFFICE_PUBLIC_BASE_URL", "")),
    })

@login_required
@require_POST
def upload_files(request):
    uploads = request.FILES.getlist("files")
    paths = request.POST.getlist("relative_paths")
    if not uploads:
        return JsonResponse({"ok": False, "error": "アップロードするファイルを選択してください。"}, status=400)
    if len(uploads) != len(paths):
        return JsonResponse({"ok": False, "error": "ファイル情報が一致しません。"}, status=400)
    created, errors = [], []
    for uploaded, raw_path in zip(uploads, paths):
        try:
            if uploaded.size > MAX_UPLOAD_BYTES:
                raise ValueError(f"{uploaded.name}: 1ファイルの上限は{MAX_UPLOAD_BYTES // (1024 * 1024)}MBです。")
            relative_path = _safe_relative_path(raw_path, uploaded.name)
            extension = os.path.splitext(uploaded.name)[1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError(f"{uploaded.name}: このファイル形式は許可されていません。")
            existing = DocumentFile.objects.filter(uploaded_by=request.user, relative_path=relative_path).first()
            if existing:
                existing.file.delete(save=False)
                existing.file.save(os.path.basename(relative_path), uploaded, save=False)
                existing.original_name = os.path.basename(relative_path)
                existing.save()
                created.append(existing.relative_path)
            else:
                item = DocumentFile(original_name=os.path.basename(relative_path), relative_path=relative_path, uploaded_by=request.user)
                item.file.save(os.path.basename(relative_path), uploaded, save=False)
                item.save()
                created.append(item.relative_path)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    return JsonResponse({"ok": not errors, "uploaded": created, "errors": errors})

@login_required
@require_GET
def file_content(request, file_id):
    item = _owned_file(request, file_id)
    try:
        handle = item.file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("ファイルが見つかりません。")
    ext = item.extension
    content_type = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp", ".txt": "text/plain; charset=utf-8", ".csv": "text/csv; charset=utf-8"}.get(ext, "application/octet-stream")
    response = FileResponse(handle, content_type=content_type)
    response["Content-Disposition"] = f'inline; filename="{secrets.token_hex(4)}{ext}"'
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response

@login_required
@require_GET
def download_file(request, file_id):
    item = _owned_file(request, file_id)
    try:
        handle = item.file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("ファイルが見つかりません。")
    response = FileResponse(handle, as_attachment=True, filename=item.original_name)
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response

@login_required
@require_POST
def delete_file(request, file_id):
    item = _owned_file(request, file_id)
    item.file.delete(save=False)
    item.delete()
    return JsonResponse({"ok": True})

@login_required
@require_GET
def excel_editor(request, file_id):
    item = _owned_file(request, file_id)
    if item.extension != ".xlsx":
        raise Http404("この編集画面は .xlsx ファイル専用です。")
    return render(request, "fileuploader/excel_editor.html", {
        "item": item,
        "content_url": reverse("fileuploader:file_content", args=[item.pk]),
        "save_url": reverse("fileuploader:excel_save", args=[item.pk]),
    })

@login_required
@require_POST
def excel_save(request, file_id):
    item = _owned_file(request, file_id)
    if item.extension != ".xlsx":
        raise Http404("この編集画面は .xlsx ファイル専用です。")
    uploaded = request.FILES.get("workbook")
    if not uploaded:
        return JsonResponse({"ok": False, "error": "保存するExcelファイルがありません。"}, status=400)
    if uploaded.size > MAX_UPLOAD_BYTES:
        return JsonResponse({"ok": False, "error": "ファイルサイズが上限を超えています。"}, status=400)
    if not uploaded.name.lower().endswith(".xlsx"):
        return JsonResponse({"ok": False, "error": ".xlsx ファイルを送信してください。"}, status=400)
    item.file.save(os.path.basename(item.relative_path), uploaded, save=False)
    item.save()
    return JsonResponse({"ok": True, "message": "Excelを保存しました。"})

@login_required
@require_GET
def office_editor(request, file_id):
    item = _owned_file(request, file_id)
    if not item.is_office_document:
        raise Http404("このファイル形式はオンライン編集に対応していません。")
    server_url = getattr(settings, "ONLYOFFICE_DOCUMENT_SERVER_URL", "")
    public_base = getattr(settings, "ONLYOFFICE_PUBLIC_BASE_URL", "").rstrip("/")
    if not server_url or not public_base:
        return render(request, "fileuploader/office_unconfigured.html", {"item": item})
    config = {
        "document": {"fileType": item.extension.lstrip("."), "key": f"doc-{item.pk}-{item.updated_at.timestamp():.0f}", "title": item.original_name,
            "url": f"{public_base}{reverse('fileuploader:file_content', args=[item.pk])}", "permissions": {"edit": True, "download": True}},
        "documentType": "word" if item.extension == ".docx" else ("cell" if item.extension == ".xlsx" else "slide"),
        "editorConfig": {"mode": "edit", "callbackUrl": f"{public_base}{reverse('fileuploader:onlyoffice_callback', args=[item.pk])}", "user": {"id": str(request.user.pk), "name": request.user.get_username()}},
    }
    return render(request, "fileuploader/office_editor.html", {"item": item, "server_url": server_url, "config_json": json.dumps(config)})

@login_required
@csrf_exempt
@require_POST
def onlyoffice_callback(request, file_id):
    # WARNING: add ONLYOFFICE JWT verification before exposing this endpoint publicly.
    item = _owned_file(request, file_id)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON")
    if payload.get("status") in (2, 6):
        download_url = payload.get("url")
        if not download_url:
            return JsonResponse({"error": 1})
        import requests
        try:
            result = requests.get(download_url, timeout=60)
            result.raise_for_status()
        except requests.RequestException:
            return JsonResponse({"error": 1})
        item.file.save(os.path.basename(item.relative_path), ContentFile(result.content), save=False)
        item.save()
    return JsonResponse({"error": 0})
