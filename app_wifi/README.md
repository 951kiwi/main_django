# app_wifi

Django app for issuing time-limited (or unlimited) QR-linked iPhone Wi-Fi configuration profile downloads.

## Install

1. Add `app_wifi` to `INSTALLED_APPS`.
2. Include `path("wifi-profiles/", include("app_wifi.urls"))` in the project URLconf.
3. Install QR dependency: `pip install "qrcode[pil]==8.2"`.
4. Configure environment variables:

```env
WIFI_SSID=your-ssid
WIFI_PASSWORD=your-wifi-password
WIFI_PROFILE_NAME=Home Wi-Fi
WIFI_ENCRYPTION_TYPE=Any
```

5. Run `python manage.py migrate`.

## URLs

- `/wifi-profiles/`: staff-only link management
- `/wifi-profiles/create/`: staff-only link creation and QR display
- `/wifi-profiles/download/<token>/`: public download landing page
- `/wifi-profiles/file/<token>/`: public mobileconfig response

Tokens are generated with a cryptographically secure random generator. Only SHA-256 token hashes are stored in the database. The raw URL is shown once at creation time. Expiration is checked on both landing and file endpoints.
