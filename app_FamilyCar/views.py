from django.shortcuts import render, redirect
from django.db.models import Sum
from datetime import date
from django.utils.timezone import now
from .forms import GasRecordForm
import calendar
from .models import GasRecord, MonthlyRecord


def gas_record_create(request):
    if request.method == 'POST':
        gas_form = GasRecordForm(request.POST)
        if gas_form.is_valid():
            # ガソリンデータの保存
            gas_form.save()
            return redirect('monthly_summary')  # 保存後にリダイレクト
    else:
        gas_form = GasRecordForm()

    return render(request, 'gasrecord_create.html', {'gas_form': gas_form})
0.

def monthly_gas_summary(request):

    monthly_data = MonthlyRecord.objects.all()

    # 月ごとのガソリン合計（走行距離）と日ごとの走行距離を取得
    monthly_summary = []
    for record in monthly_data:
        gas_datas = GasRecord.objects.filter(monthly_record=record).order_by('date')
        total_distance = gas_datas.aggregate(total_distance=Sum('distance'))['total_distance'] or 0

        monthly_summary.append({
            'month': record.month,
            'total_distance': total_distance,
            'month_data' : record,
            'gas_datas': gas_datas,
        })
    monthly_summary.sort(key=lambda x: x['month'],reverse=True)
    return render(request, 'monthly_gas_summary.html', {
        'monthly_summary': monthly_summary,
    })