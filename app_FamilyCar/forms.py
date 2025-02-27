from django import forms
from .models import GasRecord, MonthlyRecord


# GasRecord用フォーム
class GasRecordForm(forms.ModelForm):
    class Meta:
        model = GasRecord
        fields = ['date', 'distance', 'monthly_record']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # 日付用のウィジェット
        }