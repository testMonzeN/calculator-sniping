from django import forms
from django.contrib.auth.models import User

class CalculatorForm(forms.Form):
    target = forms.CharField(
        label='Размер мишени',
        widget=forms.TextInput(attrs={'class': 'small-input'})
    )
    dist = forms.CharField(
        label='Дистанция до мишени',
        widget=forms.TextInput(attrs={'class': 'small-input'})
    )


    def clean(self):
        cleaned_data = super().clean()

        target = cleaned_data.get('target')
        dist = cleaned_data.get('dist')

        return cleaned_data
        
