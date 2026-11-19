from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import Device,Command,Card
# 作成した switchbot.py から関数をインポート
from .SwitchBot import send_switchbot_command,fetch_switchbot_status
from django.views.decorators.csrf import (  # POSTをJSから叩く場合のCSRF対策（必要に応じて）
    csrf_exempt,
)
import json
from django.views.decorators.http import require_GET, require_POST
from .models import ScreenSaverMedia
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from pathlib import Path

def home(request):
    # =========================================================
    # POST: デバイスの操作リクエストを受け取ったとき
    # =========================================================
    if request.method == "POST":
        try:
            device_id = request.POST.get("device_id")
            command_name = request.POST.get("command_name")
            parameter = request.POST.get("parameter")
            device = Device.objects.get(device_id=device_id)
            # DBの Command モデルから合致するコマンドを検索
            cmd_obj = device.commands.filter(name=command_name).first()
            if not cmd_obj:
                return JsonResponse({"status": "error", "message": f"未登録のコマンド: {command_name}"}, status=400)

            # スライダー等の動的パラメータがあればそれを優先、無ければDB登録値を使用
            actual_param = parameter if parameter is not None else cmd_obj.parameter

            # SwitchBot APIへコマンド送信
            result = send_switchbot_command(device.device_id, cmd_obj.command, actual_param,cmd_obj.command_type)
            print(result)
            # 操作履歴を保存（自動で100件制限が適用されます）
            #OperationLog.objects.create(
            #    device=device,
            #    action=f"コマンド: {command}",
            #    details={"parameter": parameter, "response": result}
            #)

            return JsonResponse({"status": "success", "result": result})

        except Device.DoesNotExist:
            return JsonResponse({"status": "error", "message": "デバイスが見つかりません"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # =========================================================
    # GET: ダッシュボード画面の初期表示
    # =========================================================
    remotes = Card.objects.filter(visible=True).order_by("y", "x")
    datas = []
    for remote in remotes:
        device = remote.device
        data = {
        "x" : remote.x,
        "y" : remote.y,
        "width" : remote.width,
        "height" : remote.height,
        "type" : remote.device.device_type,
        "device_id": device.device_id if device else "",
        "features": device.features if device else [],
        "title" : remote.title,
        "sub_title" : remote.sub_title}
        datas.append(data)
    # スクリーンセイバー用メディア
    screensaver_media = []

    for media in ScreenSaverMedia.objects.filter(
        is_active=True
    ).order_by("order"):

        screensaver_media.append({
            "title": media.title,
            "type": media.media_type,
            "duration": media.duration,
            "url": media.file.url,
        })
    print(screensaver_media)
    return render(
        request,
        "smarthome/home.html",
        {
            "remotes": datas,
            "screensaver_media": screensaver_media,
        }
    )


def remote_detail(request, pk):
    remote = get_object_or_404(Card, pk=pk)

    return render(
        request,
        "remote_detail.html",
        {
            "remote": remote,
        }
    )

@require_GET
def get_all_devices_status_view(request):
    """画面上の全デバイスのステータスをまとめて返す"""
    # 表示対象のカードに紐づく device_id 一覧を取得
    devices = Device.objects.filter(card__visible=True)

    status_list = {}
    for dev in devices:
        try:
            # 各デバイスのステータスを取得
            status_list[dev.device_id] = fetch_switchbot_status(dev.device_id)
        except Exception:
            status_list[dev.device_id] = None

    return JsonResponse({"devices": status_list})

def api_status(request):
    """
    後でSwitchBot APIと接続するためのAPI。
    現在は仮のデータを返す。
    """

    data = {
        "tv": True,
        "aircon": True,
        "aircon_temperature": 24,
        "aircon_mode": "冷房",
        "aircon_fan": "自動",

        "living_light": True,
        "living_brightness": 80,

        "kitchen_light": False,
        "kitchen_brightness": 0,

        "power": 2.1,
    }

    return JsonResponse(data)

# =========================================
# スクリーンセイバー設定ページ
# =========================================

@require_http_methods(["GET", "POST"])
def screensaver_settings(request):

    if request.method == "POST":

        action = request.POST.get("action")

        
        # -----------------------------
        # メディアアップロード
        # -----------------------------

        if action == "upload":

            is_ajax = (
                request.headers.get("X-Requested-With")
                == "XMLHttpRequest"
            )

            def upload_response(success, message, status=200):
                if is_ajax:
                    return JsonResponse({
                        "success": success,
                        "message": message,
                    }, status=status)

                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

                return redirect("screensaver_settings")

            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return upload_response(
                    False,
                    "ファイルを選択してください。",
                    400
                )

            if uploaded_file.size > 500 * 1024 * 1024:
                return upload_response(
                    False,
                    "ファイルは500MB以下にしてください。",
                    400
                )

            ext = Path(uploaded_file.name).suffix.lower()

            image_ext = [
                ".jpg", ".jpeg", ".png", ".webp", ".gif"
            ]

            video_ext = [
                ".mp4", ".webm", ".mov"
            ]

            if ext in image_ext:
                media_type = "image"

            elif ext in video_ext:
                media_type = "video"

            else:
                return upload_response(
                    False,
                    "対応していないファイル形式です。",
                    400
                )

            title = Path(uploaded_file.name).stem

            try:

                ScreenSaverMedia.objects.create(
                    title=title,
                    media_type=media_type,
                    file=uploaded_file,
                    is_active=True,
                    order=(
                        ScreenSaverMedia.objects.count() + 1
                    ),
                    duration=10
                )

                return upload_response(
                    True,
                    f"{title} を追加しました。"
                )

            except Exception as error:

                print(
                    "ScreenSaver upload error:",
                    error
                )

                return upload_response(
                    False,
                    "ファイルの保存に失敗しました。",
                    500
                )


        # -----------------------------
        # 削除
        # -----------------------------

        elif action == "delete":

            media_id = request.POST.get("media_id")

            media = get_object_or_404(
                ScreenSaverMedia,
                pk=media_id
            )

            if media.file:
                media.file.delete(save=False)

            media.delete()

            messages.success(request, "削除しました。")

        # -----------------------------
        # 有効・無効
        # -----------------------------

        elif action == "toggle":

            media = get_object_or_404(
                ScreenSaverMedia,
                pk=request.POST.get("media_id")
            )

            media.is_active = not media.is_active
            media.save(update_fields=["is_active"])

            messages.success(request, "設定を変更しました。")

        # -----------------------------
        # 画像表示時間変更
        # -----------------------------

        elif action == "duration":

            media = get_object_or_404(
                ScreenSaverMedia,
                pk=request.POST.get("media_id")
            )

            if media.media_type == "image":
                try:
                    duration = int(request.POST.get("duration", 10))

                    if 1 <= duration <= 3600:
                        media.duration = duration
                        media.save(update_fields=["duration"])
                        messages.success(request, "表示時間を変更しました。")
                    else:
                        messages.error(request, "1〜3600秒で指定してください。")

                except (ValueError, TypeError):
                    messages.error(request, "秒数が正しくありません。")

        return redirect("screensaver_settings")

    # -----------------------------
    # GET: 一覧表示
    # -----------------------------

    media_list = ScreenSaverMedia.objects.all()

    print(media_list)
    context = {
        "media_list": media_list,
        "image_count": media_list.filter(media_type="image").count(),
        "video_count": media_list.filter(media_type="video").count(),
        "active_count": media_list.filter(is_active=True).count(),
    }

    return render(
        request,
        "smarthome/screensaver_settings.html",
        context
    )