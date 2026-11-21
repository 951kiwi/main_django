from datetime import datetime, time, timedelta

from django import forms
from django.utils import timezone


class WifiProfileCreateForm(forms.Form):
    EXPIRY_CHOICES = [
        ("1", "1日間"),
        ("7", "7日間"),
        ("30", "30日間"),
        ("90", "90日間"),
        ("custom", "日付を指定"),
        ("unlimited", "無制限"),
    ]

    expiry = forms.ChoiceField(
        choices=EXPIRY_CHOICES,
        initial="7",
        label="リンクの有効期限",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    custom_date = forms.DateField(
        required=False,
        label="有効期限の日付",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    def clean(self):
        cleaned = super().clean()
        expiry = cleaned.get("expiry")
        custom_date = cleaned.get("custom_date")
        today = timezone.localdate()

        if expiry == "custom":
            if not custom_date:
                self.add_error("custom_date", "有効期限の日付を指定してください。")
            elif custom_date < today:
                self.add_error("custom_date", "今日以降の日付を指定してください。")
        return cleaned

    def get_expires_at(self):
        expiry = self.cleaned_data["expiry"]
        if expiry == "unlimited":
            return None
        if expiry == "custom":
            target = self.cleaned_data["custom_date"]
            local_dt = datetime.combine(target, time(23, 59, 59))
            return timezone.make_aware(local_dt, timezone.get_current_timezone())
        days = int(expiry)
        return timezone.now() + timedelta(days=days)
