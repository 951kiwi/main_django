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
    """
    Receive SwitchBot webhook events.

    Configure SWITCHBOT_WEBHOOK_SECRET in the server environment and register
    the callback URL containing the same secret.
    """
    expected_secret = os.getenv("SWITCHBOT_WEBHOOK_SECRET", "")

    # Fail closed: never accept webhook requests if the secret is not configured.
    if not expected_secret or not hmac.compare_digest(secret, expected_secret):
        return JsonResponse({"success": False, "error": "Forbidden"}, status=403)

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

    # Keep the initial receiver independent from device-control logic.
    # The event can be routed to services / models after its real payload is confirmed.
    logger.info(
        "SwitchBot webhook received: eventType=%s eventVersion=%s",
        payload.get("eventType", "unknown"),
        payload.get("eventVersion", "unknown"),
    )
    logger.debug("SwitchBot webhook payload: %s", json.dumps(payload, ensure_ascii=False))

    return JsonResponse({"success": True})
