from django.core.management.base import BaseCommand
from django.utils import timezone
from app_smarthome.models import Device, DailyPowerConsumption
from app_smarthome.SwitchBot import get_device_status  # status取得関数

class Command(BaseCommand):
    help = "プラグの当日消費電力を集計・保存"

    def handle(self, *args, **options):
        today = timezone.localdate()
        devices = Device.objects.filter(device_type__in=["concent", "plug"])

        for dev in devices:
            res = get_device_status(dev.device_id)
            if res.get("statusCode") == 100:
                body = res.get("body", {})
                # Wh から kWh に換算
                wh = body.get("electricityOfDay", 0)
                kwh = round(wh / 1000.0, 3)

                DailyPowerConsumption.objects.update_or_create(
                    device=dev,
                    date=today,
                    defaults={"power_kwh": kwh}
                )
                self.stdout.write(f"[{dev.name}] {today}: {kwh} kWh 記録完了")