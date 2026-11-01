
import os

from django.core.management.base import BaseCommand, CommandError

from app_smarthome.SwitchBot import setup_switchbot_webhook


class Command(BaseCommand):
    help = "Register the SwitchBot webhook callback URL"

    def handle(self, *args, **options):
        secret = os.getenv("SWITCHBOT_WEBHOOK_SECRET")

        if not secret:
            raise CommandError(
                "SWITCHBOT_WEBHOOK_SECRET is not configured."
            )

        callback_url = (
            "https://951kiwi.com"
            f"/smarthome/api/switchbot/webhook/{secret}/"
        )

        try:
            result = setup_switchbot_webhook(callback_url)
        except Exception as exc:
            raise CommandError(
                f"Webhook registration failed: {exc}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"SwitchBot Webhook registration response: {result}"
            )
        )
