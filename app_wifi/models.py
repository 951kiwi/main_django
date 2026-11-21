from django.conf import settings
from django.db import models


class WifiProfileLink(models.Model):
    token_hash = models.CharField(max_length=64, unique=True, db_index=True, verbose_name="トークンハッシュ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="発行日時")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="有効期限")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wifi_profile_links",
        verbose_name="発行者",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Wi-Fi配布リンク"
        verbose_name_plural = "Wi-Fi配布リンク"

    def __str__(self):
        return f"Wi-Fiリンク #{self.pk}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at is not None and self.expires_at <= timezone.now()

    @property
    def is_available(self):
        return self.is_active and not self.is_expired
