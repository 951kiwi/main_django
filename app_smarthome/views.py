from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import Device,Command,Card
# 作成した switchbot.py から関数をインポート
from .SwitchBot import send_switchbot_command
import json

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
    return render(
        request,
        "smarthome/home.html",
        {
            "remotes": datas,
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