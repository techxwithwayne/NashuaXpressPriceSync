from django import forms

from .models import PriceList

class pricelistform(forms.Form):
    class meta:
        model = PriceList
        fields = '__all__'