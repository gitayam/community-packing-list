from django import forms
from .models import Price

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['price', 'store_name', 'submitted_by_name']
