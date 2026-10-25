# app_fileuploader — private file manager

## Features
- Existing Django login required for manager, upload, preview, download, delete, and editor pages.
- Per-user file lists and ownership checks.
- Folder upload preserving browser-provided relative paths.
- Authenticated PDF/image preview; managed files are stored under `MEDIA_ROOT/fileuploads/` like the rest of the project's media files.
- Other allowed files are downloadable.
- Basic in-browser XLSX editing via SheetJS CDN; saves the workbook under `MEDIA_ROOT/fileuploads/`. The formula bar shows a cell's formula (when present) or value.
- Optional ONLYOFFICE Docs editor integration for DOCX/PPTX.

## Install / update
Run from the project directory:

```powershell
python manage.py migrate
python manage.py check
```

No change to `main/urls.py` is needed; the existing `/fileuploader/` include already points to this app.

## Upload size
Default limit is 100 MiB per file. Override in settings.py with `FILEUPLOADER_MAX_UPLOAD_BYTES`.

## Simple Excel editor
Open an `.xlsx` file and choose **Excel編集**. It uses SheetJS from a CDN, so no Python package, database migration, Docker, or separate office server is needed.

This is a lightweight editor, not a full Excel replacement. Formula text is retained and shown in the formula bar, but formulas are not recalculated in the browser; Excel recalculates them when the workbook is opened. Formatting, charts, merged cells, macros, and other advanced workbook features may not round-trip exactly. Keep a backup of important workbooks before saving. Internet access is required to load the SheetJS script.

## ONLYOFFICE
Set these environment variables (for example in the local .env, never commit secrets):
- `ONLYOFFICE_DOCUMENT_SERVER_URL`: browser-accessible Document Server URL, e.g. `http://localhost:8080`
- `ONLYOFFICE_PUBLIC_BASE_URL`: URL that the ONLYOFFICE server/container can use to reach Django

Important: the callback endpoint currently does not verify ONLYOFFICE JWT signatures. Keep the service on a trusted private network and do not expose it publicly until JWT validation and network restrictions are configured. Editing is disabled until these variables are set. Save callbacks require the Django server to be reachable from the Document Server, and the Document Server must be able to fetch the authenticated file content URL. For deployments where the Document Server cannot use the user's session cookie, use a short-lived signed file URL/token instead of exposing a public endpoint.

## Security notes
- File contents are not linked through `MEDIA_URL`.
- All file operations are restricted to the logged-in owner.
- The upload endpoint allows a small allowlist of extensions and rejects path traversal.
- Use HTTPS and a strong Django SECRET_KEY when accessing over a network.
