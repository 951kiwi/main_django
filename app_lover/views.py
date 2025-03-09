from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Selection
import requests
from bs4 import BeautifulSoup

#ハーゲンダッツのjancodeリスト
urls = ['https://www.jancode.xyz/corp/?c=29119','https://www.jancode.xyz/corp/?c=29119&p=2',
       'https://www.jancode.xyz/corp/?c=29119&p=3','https://www.jancode.xyz/corp/?c=29119&p=4'
       ,'https://www.jancode.xyz/corp/?c=29119&p=5','https://www.jancode.xyz/corp/?c=29119&p=6'
       ,'https://www.jancode.xyz/corp/?c=29119&p=7']
# ヘッダー情報（アクセスブロックを回避するため）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}


def phone_view(request):
    # 最初のSelectionオブジェクトを取得
    selection = Selection.objects.first()
    if request.method == "POST":
        data = request.POST.get("message")
        if(data == "Q01=True"):
            selection.game01 = True
            selection.save()
        if(data == "Q02=True"):
            selection.game02 = True
            selection.save()
        ##if(data == "Q03=True"): 使わない
        ##    selection.game03 = True
        ##    selection.save()
        if(data == "Q04=True"):
            selection.game04 = True
            selection.save()
        if(data == "Q05=True"):
            selection.game05 = True
            selection.save()
        if(data == "Q06=True"):
            selection.game06 = True
            selection.save()
        if(data == "Q04=Jan"):
            jancode = request.POST.get("jancode")
            # ページの取得
            print(jancode)
        else:
            return JsonResponse({"status": "error"})  # JSONレスポンスを返す
        return JsonResponse({"status": "success"})  # JSONレスポンスを返す
        

    if(selection.login == True):
        if(selection.gamestart == True):
            return render(request, 'phone_Q.html',context={"data":selection})
        return render(request, 'phone_sucsess.html',context={"data":selection})
    return render(request, 'phone.html')

def Q3_QR(request):
    selection = Selection.objects.first()
    selection.game03 = True
    selection.save()
    return render(request, 'Q3_QRload.html',context={"data":selection})

def PC_view(request):
    selection = Selection.objects.first()
    if request.method == "POST":
        data = request.POST.get("message")
        print(data)
        if(data == "gamestart"):
            selection.gamestart = True
            selection.save()
        return JsonResponse({"status": "success"})  # JSONレスポンスを返す
    
    if(selection.login == True):
        if(selection.gamestart == True):
            return render(request, 'PC_startgame.html',context={"data":selection})
        return render(request, 'PC_main01.html')
    return render(request, 'PC_main.html')

def phone_name_birthday(request):
    if request.method == 'POST':
        # フォームからデータを取得
        name = request.POST.get('name')
        birth_date = request.POST.get('birth_date')
        # 最初のSelectionオブジェクトを取得
        selection = Selection.objects.first()

        if selection:
            selection.name = name
            selection.birth_date = birth_date
            selection.login = True
            selection.save()
    return redirect('phone')

def phone_data_save(request):
    if request.method == 'POST':
        # フォームからデータを取得
        gamestart = request.POST.get('gamestart')
        game01 = request.POST.get('game01')
        game02 = request.POST.get('game02')
        game03 = request.POST.get('game03')
        game04 = request.POST.get('game04')
        game05 = request.POST.get('game05')
        game06 = request.POST.get('game06')
        # 最初のSelectionオブジェクトを取得
        selection = Selection.objects.first()

        if selection:
            if(gamestart):
                selection.gamestart = gamestart
            if(game01):
                selection.game01 = game01
            if(game02):
                selection.game02 = game02
            if(game03):
                selection.game03 = game03
            if(game04):
                selection.game04 = game04
            if(game05):
                selection.game05 = game05
            if(game06):
                selection.game06 = game06
            
            selection.save()
    return redirect('phone')


def get_data(request):
    data = Selection.objects.first()
    response_data = {
        "id": data.id,
        "name": data.name,
        "login": data.login,
        "gamestart":data.gamestart,
        "game01": data.game01,
        "game02": data.game02,
        "game03": data.game03,
        "game04": data.game04,
        "game05": data.game05,
        "game06": data.game06,
    }
    return JsonResponse(response_data)
