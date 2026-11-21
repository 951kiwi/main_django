import hashlib
import io
import plistlib
import secrets
import uuid
import base64

import qrcode
from django.conf import settings


def create_raw_token():
    return secrets.token_urlsafe(32)


def hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def build_mobileconfig():
    ssid = getattr(settings, "WIFI_SSID", "")
    password = getattr(settings, "WIFI_PASSWORD", "")
    encryption = getattr(settings, "WIFI_ENCRYPTION_TYPE", "Any")

    if not ssid or not password:
        raise ValueError("WIFI_SSID と WIFI_PASSWORD を .env に設定してください。")

    wifi_payload = {
        "PayloadType": "com.apple.wifi.managed",
        "PayloadVersion": 1,
        "PayloadIdentifier": f"{settings.SECRET_KEY[:12]}.wifi",
        "PayloadUUID": str(uuid.uuid4()).upper(),
        "PayloadDisplayName": f"{ssid} Wi-Fi",
        "SSID_STR": ssid,
        "HIDDEN_NETWORK": False,
        "AutoJoin": True,
        "EncryptionType": encryption,
        "Password": password,
    }
    profile = {
        "PayloadType": "Configuration",
        "PayloadVersion": 1,
        "PayloadIdentifier": f"{settings.SECRET_KEY[:12]}.wifi.profile",
        "PayloadUUID": str(uuid.uuid4()).upper(),
        "PayloadDisplayName": getattr(settings, "WIFI_PROFILE_NAME", "Wi-Fi接続設定"),
        "PayloadDescription": "Wi-Fi接続用プロファイルです。",
        "PayloadOrganization": "Personal",
        "PayloadRemovalDisallowed": False,
        "PayloadContent": [wifi_payload],
    }
    return plistlib.dumps(profile, fmt=plistlib.FMT_XML, sort_keys=False)


def make_qr_data_uri(value):
    image = qrcode.make(value, box_size=8, border=3)
    output = io.BytesIO()
    image.save(output, format="PNG")
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
