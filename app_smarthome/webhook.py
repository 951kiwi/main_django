
import hmac
import json
import logging
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def switchbot_webhook(request, secret):
    expected_secret = os.getenv("SWITCHBOT_WEBHOOK_SECRET", "")

    # 秘密トークンが未設定、または一致しない場合は拒否
    if not expected_secret or not hmac.compare_digest(
        secret, expected_secret
    ):
        return JsonResponse(
            {"success": False, "error": "Forbidden"},
            status=403,
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400,
        )

    if not isinstance(payload, dict):
        return JsonResponse(
            {"success": False, "error": "JSON object required"},
            status=400,
        )

    logger.info(
        "SwitchBot webhook received: eventType=%s eventVersion=%s",
        payload.get("eventType", "unknown"),
        payload.get("eventVersion", "unknown"),
    )

    logger.debug(
        "SwitchBot webhook payload: %s",
        json.dumps(payload, ensure_ascii=False),
    )

    return JsonResponse({"success": True})
