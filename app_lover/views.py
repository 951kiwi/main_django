from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Selection

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
        "game01": data.game01,
        "game02": data.game02,
        "game03": data.game03,
        "game04": data.game04,
        "game05": data.game05,
        "game06": data.game06,
    }
    return JsonResponse(response_data)
