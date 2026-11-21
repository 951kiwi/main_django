from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.cache import never_cache

from .forms import WifiProfileCreateForm
from .models import WifiProfileLink
from .services import build_mobileconfig, create_raw_token, hash_token, make_qr_data_uri


def staff_required(view_func):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="/login/")(view_func)


@staff_required
@require_GET
def profile_list(request):
    links = WifiProfileLink.objects.select_related("created_by").all()
    return render(request, "app_wifi/profile_list.html", {"links": links})


@staff_required
@require_POST
def disable_link(request, pk):
    link = get_object_or_404(WifiProfileLink, pk=pk)
    link.is_active = False
    link.save(update_fields=["is_active"])
    messages.success(request, "ダウンロードリンクを無効化しました。")
    return redirect("app_wifi:profile_list")


@staff_required
@require_http_methods(["GET", "POST"])
def create_link(request):
    if request.method == "POST":
        form = WifiProfileCreateForm(request.POST)
        if form.is_valid():
            raw_token = create_raw_token()
            link = WifiProfileLink.objects.create(
                token_hash=hash_token(raw_token),
                expires_at=form.get_expires_at(),
                created_by=request.user,
            )
            download_path = reverse("app_wifi:download_page", kwargs={"token": raw_token})
            if settings.DEBUG:
                download_url = request.build_absolute_uri(download_path)
            else:
                # Nginx等のリバースプロキシ配下でもQRコードは必ずHTTPSにする
                download_url = f"https://{request.get_host()}{download_path}"
            return render(request, "app_wifi/link_created.html", {
                "link": link,
                "download_url": download_url,
                "qr_data_uri": make_qr_data_uri(download_url),
            })
    else:
        form = WifiProfileCreateForm()
    return render(request, "app_wifi/create_link.html", {"form": form})


@require_GET
@never_cache
def download_page(request, token):
    link = get_object_or_404(WifiProfileLink, token_hash=hash_token(token))
    if not link.is_available:
        return render(request, "app_wifi/link_unavailable.html", status=410)
    return render(request, "app_wifi/download.html", {"profile_name": settings.WIFI_PROFILE_NAME, "download_url": reverse("app_wifi:download_profile", kwargs={"token": token})})


@require_GET
@never_cache
def download_profile(request, token):
    link = get_object_or_404(WifiProfileLink, token_hash=hash_token(token))
    if not link.is_available:
        raise Http404("このダウンロードリンクは無効または期限切れです。")
    try:
        content = build_mobileconfig()
    except ValueError as exc:
        return HttpResponse(str(exc), status=503, content_type="text/plain; charset=utf-8")

    response = HttpResponse(content, content_type="application/x-apple-aspen-config")
    response["Content-Disposition"] = 'attachment; filename="wifi-profile.mobileconfig"'
    response["Cache-Control"] = "private, no-store, max-age=0"
    response["Pragma"] = "no-cache"
    response["X-Content-Type-Options"] = "nosniff"
    return response
