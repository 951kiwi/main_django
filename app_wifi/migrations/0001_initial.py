import django.conf
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="WifiProfileLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(db_index=True, max_length=64, unique=True, verbose_name="トークンハッシュ")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="発行日時")),
                ("expires_at", models.DateTimeField(blank=True, null=True, verbose_name="有効期限")),
                ("is_active", models.BooleanField(default=True, verbose_name="有効")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="wifi_profile_links", to=django.conf.settings.AUTH_USER_MODEL, verbose_name="発行者")),
            ],
            options={"verbose_name": "Wi-Fi配布リンク", "verbose_name_plural": "Wi-Fi配布リンク", "ordering": ["-created_at"]},
        ),
    ]
