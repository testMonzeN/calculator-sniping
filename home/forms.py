from django import forms
from django.contrib.auth.models import User

class CalculatorForm(forms.Form):
    target = forms.CharField(
        label='Размер мишени',
        help_text='В метрах'
    )
    dist = forms.CharField(
        label='Дистанция до мишени',
        help_text='от 100м до 1500м'
    )


    def clean(self):
        cleaned_data = super().clean()

        target = cleaned_data.get('target')
        dist = cleaned_data.get('dist')

        return cleaned_data
        
