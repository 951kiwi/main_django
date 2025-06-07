from django import forms
from .models import GasRecord, MonthlyRecord

# GasRecord用フォーム
class GasRecordForm(forms.ModelForm):
    class Meta:
        model = GasRecord
        fields = ['user','date', 'distance', 'monthly_record','image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # 日付用のウィジェット
            'distance': forms.NumberInput(attrs={'min': '0'}),  # ← ここを追加
        }