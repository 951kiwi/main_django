from django.shortcuts import render, redirect
from django.db.models import Sum
from datetime import date
from django.utils.timezone import now
from .forms import GasRecordForm
from django.contrib.auth import get_user_model
import calendar
from .models import GasRecord, MonthlyRecord
from django.contrib.auth.decorators import login_required


def user_permission(request):
    user = request.user
    if not user.is_authenticated:
        permission =  'anonymous'  # 未ログインの場合
    elif user.username == "951kiwi":
        permission = 'admin'
    elif user.username == 'miu':
        permission = 'general'
    elif user.username == 'daiki':
        permission = 'parent'

    return permission

def gas_record_create(request):
    if request.method == 'POST': #保存なら
        gas_form = GasRecordForm(request.POST)
        if gas_form.is_valid():
            # ガソリンデータの保存
            gas_form.save()
            return redirect('monthly_summary')  # 保存後にリダイレクト
    else:
        # 初期値にログイン中のユーザーを設定
        form = GasRecordForm(initial={'user': request.user, 'date': now().date()})

    return render(request, 'FamilyCar/gasrecord_create.html', {'gas_form': form,'permission':user_permission(request)})

def parent_monthly_summary(request):
    monthly_data = MonthlyRecord.objects.all()
    User = get_user_model()
    # 月ごとのガソリン合計（走行距離）と日ごとの走行距離を取得
    childUsersId=[1,5] # 1=あいむ 5=みう
    monthly_summary = []
    
    for record in monthly_data:
        datas = []
        for userId in childUsersId:
            try:
                user = User.objects.get(id=userId)
            except User.DoesNotExist:
                continue  # ユーザーが見つからなければスキップ

            gas_datas = GasRecord.objects.filter(monthly_record=record,user = user).order_by('date')
            total_distance = gas_datas.aggregate(total_distance=Sum('distance'))['total_distance'] or 0
            username = user.nickname
            if username == None:
                username = user.username
            datas.append({
                'name' : username,
                'total_distance': total_distance,
                'gas_datas': gas_datas,
            })
        monthly_summary.append({
            'month': record.month,
            'month_data' : record,
            "datas" : datas
        })
    monthly_summary.sort(key=lambda x: x['month'],reverse=True)
    return render(request, 'FamilyCar/parent_monthly_summmary.html', {
        'monthly_summary': monthly_summary,
    })



@login_required
def monthly_gas_summary(request):

    monthly_data = MonthlyRecord.objects.all()
    user = request.user
    permission = user_permission(request)
    print(permission)
    if permission == "parent":
        return redirect('parent_monthly_summary')  # 保存後にリダイレクト
    

    # 月ごとのガソリン合計（走行距離）と日ごとの走行距離を取得
    monthly_summary = []
    for record in monthly_data:
        gas_datas = GasRecord.objects.filter(monthly_record=record , user=user).order_by('date')
        total_distance = gas_datas.aggregate(total_distance=Sum('distance'))['total_distance'] or 0

        monthly_summary.append({
            'month': record.month,
            'total_distance': total_distance,
            'month_data' : record,
            'gas_datas': gas_datas,
        })
    monthly_summary.sort(key=lambda x: x['month'],reverse=True)
    return render(request, 'FamilyCar/monthly_gas_summary.html', {
        'monthly_summary': monthly_summary,
    })
