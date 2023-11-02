from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import PriceList, ExchangeRate, ProductCostingFactors, ProductCostMapping

#create forms below
class pricelistform(ModelForm):
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



class Userform(forms.Form):
    class meta:
        model = User
        fields = ['username', 'password']
        # create labels, widgets dictionary
        labels = {
            'username': '',
            'password': ''
        }
       
        widgets = {
            'username': forms.DateInput(attrs={'class':'form-control', 'type':'date', 'required':'required'}),
            'password': forms.TextInput(attrs={'class':'form-control', 'id':'decimalInput', 'oninput':"validateDecimal(this)", 'required':'required'})
        }

class UpdateProductCostingFactorsForm(forms.Form):
    class meta:
        model = ProductCostingFactors
        fields = '__all__'



class UpdateProductCostingFactorsForm(forms.Form):
    class Meta:
        model = ProductCostingFactors
        exclude = ['StockCategory'] 

class UpdateProductCostMappingForm(forms.Form):
    class Meta:
        model = ProductCostMapping
        exclude = ['StockCategory'] 
'''
        prodID
prodSupplierCode
prodNashuaCode
prodDesc
prodCategory
prodSupplierName
prodSupplierCurrency
prodCalculationModifier
prodSupplierCost
prodSupplierCostUSD
prodSupplierLandedCost_USD
prodNashuaSellingPrice_USD
prodCalculatedPriceDatex
'''

# spot the difference between ModelForm and forms.Form
class ProductCostingFactorsform(forms.Form):
    class meta:
        model = ProductCostingFactors
        fields = '__all__'
    '''
    currency_choices = [('ZAR', 'ZAR'), ('ZWL', 'ZWL'),('USD', 'USD')]
    cf_currency = forms.ChoiceField(
        choices=currency_choices,
        widget=forms.Select(attrs={'class': 'form-control col-lg-6 col-sm-12 col-12'}),label='Currency')
    
    customer_name_choices = [('TAROPA', 'TAROPA'), ('ZEPO', 'ZEPO')]
    cf_supplier_name = forms.ChoiceField(
        choices=customer_name_choices,
        widget=forms.Select(attrs={'class': 'form-control col-lg-12 col-sm-12 col-12'}),label='Customer Name')
    
    category_choices = [('MAIZE', 'MAIZE')]
    cf_category = forms.ChoiceField(
        choices=category_choices,
        widget=forms.Select(attrs={'class': 'form-control col-lg-6 col-sm-12 col-12'}),label='Category')
    
    class Meta:
        model = ProductCostingFactors
        fields = ['ExchangeRateFactor', 'DutyFactor', 'FreightChargesFactor', 'MarkupFactor']
        # create labels, widgets dictionary
        labels = {
            'ExchangeRateFactor': 'Exchange Rate',
            'DutyFactor': 'Duty Factor',
            'FreightChargesFactor': 'Freight Charges',
            'MarkupFactor': 'Markup Factor'
        }
       
        widgets = {
            'ExchangeRateFactor': forms.TextInput(attrs={'class':'form-control', 'id':'decimalInput', 'oninput':"validateDecimal(this)", 'required':'required'}),
            'DutyFactor': forms.TextInput(attrs={'class':'form-control', 'id':'decimalInput', 'oninput':"validateDecimal(this)", 'required':'required'}),
            'FreightChargesFactor': forms.TextInput(attrs={'class':'form-control', 'id':'decimalInput', 'oninput':"validateDecimal(this)", 'required':'required'}),
            'MarkupFactor': forms.TextInput(attrs={'class':'form-control', 'id':'decimalInput', 'oninput':"validateDecimal(this)", 'required':'required'})
        }

        '''


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    bool_choice = [('True', 'True'), ('False', 'False')]


    is_staff = forms.ChoiceField(
        choices=bool_choice,
        widget=forms.Select(attrs={'class': 'form-control col-lg-6 col-sm-12 col-12'}),label='Is user staff')
    
    is_active = forms.ChoiceField(
        choices=bool_choice,
        widget=forms.Select(attrs={'class': 'form-control col-lg-6 col-sm-12 col-12'}),label='Is account active')
    
    is_superuser = forms.ChoiceField(
        choices=bool_choice,
        widget=forms.Select(attrs={'class': 'form-control col-lg-6 col-sm-12 col-12'}),label='Is account administrative')

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "is_staff", "is_active", "is_superuser", "email", "password1", "password2"]

       
        widgets = {
            'email': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
            'first_name': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
            'last_name': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
            'username': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
            'password1': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
            'password2': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
        }
