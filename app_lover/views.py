from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Selection

def phone_view(request):
    # 最初のSelectionオブジェクトを取得
    selection = Selection.objects.first()
    if(selection.login == True):
        return render(request, 'phone_sucsess.html',context={"data":selection})

    return render(request, 'phone.html')

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

def get_data(request):
    data = Selection.objects.first()
    response_data = {
        "id": data.id,
        "name": data.name,
        "game01": data.game01,
        "game02": data.game02,
        "game03": data.game03,
        "game04": data.game04,
        "game05": data.game05,
        "game06": data.game06,
    }
    return JsonResponse(response_data)
