from django import forms
from .models import Selection

class SelectionForm(forms.ModelForm):
    class Meta:
        model = Selection
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 「あり」の場合のみチェックボックスを表示
        if not self.instance.resume_required:
            self.fields['resume_submitted'].widget = forms.HiddenInput()
        if not self.instance.aptitude_test_required:
            self.fields['aptitude_test_taken'].widget = forms.HiddenInput()
        if not self.instance.web_test_required:
            self.fields['web_test_taken'].widget = forms.HiddenInput()
