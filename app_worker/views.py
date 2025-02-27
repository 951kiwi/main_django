from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Selection
from .forms import SelectionForm
from django.db.models import Case, When, Value, IntegerField

def selection_list(request):
    selections = Selection.objects.all().order_by('company_name')  # 企業名順にソート
    selections = selections.order_by(
        Case(
            When(interview_status="rejected", then=Value(1)),  # "落ちた" を最後に
            default=Value(0),  # それ以外の企業は先に
            output_field=IntegerField(),  # 整数として出力
        )
    )
    for i in selections:
        print(i.interview_status)
    return render(request, "selection_list.html", {"selections": selections})


def update_status(request, pk):
    """ AJAXで即時更新する """
    selection = get_object_or_404(Selection, pk=pk)
    field = request.POST.get("field")
    value = request.POST.get("value")

    if field in ["resume_submitted", "aptitude_test_taken", "web_test_taken"]:
        value = value == "true"
        if value == "true":
            value = True
        elif value == "False":
            value = False
    
    elif field == "interview_status":
        if value not in dict(selection.SelectionStatus.choices):
            return JsonResponse({"success": False})
    elif field == "memo":
        selection.memo = value
        selection.save()
        return JsonResponse({"success": True})

    setattr(selection, field, value)
    selection.save()
    return JsonResponse({"success": True})

def selection_create(request):
    """ 新規作成 """
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('selection_list')
    else:
        form = SelectionForm()
    return render(request, 'selection_form.html', {'form': form})

def selection_edit(request, pk):
    """ 編集ページ """
    selection = get_object_or_404(Selection, pk=pk)
    if request.method == 'POST':
        form = SelectionForm(request.POST, instance=selection)
        if form.is_valid():
            form.save()
            return redirect('selection_list')
    else:
        form = SelectionForm(instance=selection)
    return render(request, 'selection_form.html', {'form': form, 'editing': True})

def selection_delete(request, pk):
    """ 削除 """
    selection = get_object_or_404(Selection, pk=pk)
    
    if request.method == 'POST':
        # 削除処理
        selection.delete()
        return redirect('selection_list')  # 削除後、リストページにリダイレクト

    return render(request, 'selection_confirm_delete.html', {'selection': selection})