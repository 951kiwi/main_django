import os
import time
import hmac
import hashlib
import base64
import uuid
import requests

def get_switchbot_headers():
    token = os.getenv("SWITCHBOT_TOKEN")
    secret = os.getenv("SWITCHBOT_SECRET")

    if not token or not secret:
        raise ValueError("SwitchBot credentials are not set in environment variables.")

    nonce = str(uuid.uuid4())
    t = str(int(round(time.time() * 1000)))
    string_to_sign = f"{token}{t}{nonce}".encode("utf-8")

    secret_b = secret.encode("utf-8")
    sign = base64.b64encode(
        hmac.new(secret_b, msg=string_to_sign, digestmod=hashlib.sha256).digest()
    ).decode("utf-8")

    return {
        "Authorization": token,
        "sign": sign,
        "nonce": nonce,
        "t": t,
        "Content-Type": "application/json; charset=utf8",
    }

def send_switchbot_command(device_id: str, command: str, parameter: str = "default", command_type: str = "command"):
    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/commands"
    headers = get_switchbot_headers()
    payload = {
        "command": command,
        "parameter": parameter,
        "commandType": command_type,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=5)
    return response.json()