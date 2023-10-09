from django import forms
from django.forms import ModelForm
from .models import PriceList, ExchangeRate

#create forms below
class pricelistform(forms.Form):
    class meta:
        model = PriceList
        fields = '__all__'


class ExchangeRateForm(ModelForm):
    rbc_choices = [('USD', 'USD'), ('ZAR', 'ZAR'), ('ZWL', 'ZWL')]
    rateBaseCurrency = forms.ChoiceField(
        choices=rbc_choices,
        widget=forms.Select(attrs={'class': 'form-control'}),label='Source Currency')
    
    rtc_choices = [('ZWL', 'ZWL'), ('USD', 'USD'), ('ZAR', 'ZAR')]
    rateTargetCurrency = forms.ChoiceField(
        choices=rtc_choices,
        widget=forms.Select(attrs={'class': 'form-control'}),label='Target Currency')
    
    class Meta:
        model = ExchangeRate
        fields = ['rateDate', 'rateBaseCurrency', 'rateTargetCurrency', 'rateValue']
        # create labels, widgets dictionary
        labels = {
            'rateDate': 'Date of Exchange Rate',
            'rateValue': 'Conversion Rate'
        }
       
        widgets = {
            'rateDate': forms.DateInput(attrs={'class':'form-control', 'type':'date', 'required':'required'}),
            'rateValue': forms.TextInput(attrs={'class':'form-control', 'id':'decimalInput', 'oninput':"validateDecimal(this)", 'required':'required'})
        }

        

