from django.shortcuts import render
from django.http import HttpResponse
from tablib import Dataset
from .models import PriceList, ExchangeRate
from .resources import pricelistResource
from .db_utils import get_db_connection
from datetime import datetime
import pyodbc





# create your views here
def dashboard(request):
    return render(request, 'ps_blocks/dashboard.html')
    #return HttpResponse("Hello World")

def login(request):
    return render(request, 'ps_blocks/login.html')

def forgotpassword(request):
    return render(request, 'forgot-password.html')

def signup(request):
    return render(request, 'ps_blocks/signup.html')

def rateupdate(request):
    if request.method == 'POST':
        if request.POST.get('ratedate') and request.POST.get('basecurrency') and request.POST.get('targetcurrency') and request.POST.get('ratevalue'):
            # Create a datetime object
            current_datetime = datetime.now()
            current_datetime_str = str(current_datetime)
            insertdexrate = ExchangeRate()
            insertdexrate.rateDate = request.POST.get('ratedate')
            insertdexrate.rateBaseCurrency = request.POST.get('basecurrency')
            insertdexrate.rateTargetCurrency = request.POST.get('targetcurrency')
            insertdexrate.rateValue = request.POST.get('ratevalue')
            insertdexrate.rateUpdatedBy = "Keegan Solomon"
            insertdexrate.rateUpdatedOn = current_datetime_str
            # Query the database to check if the values exist
            if ExchangeRate.objects.filter(rateDate=request.POST.get('ratedate'), rateBaseCurrency=request.POST.get('basecurrency'), rateTargetCurrency=request.POST.get('targetcurrency')).exists():
                # Values already exist in the database, return JavaScript alert
                alert_message = "Values already exist in the database!"
                js_code = f"alert('{alert_message}');"
                return HttpResponse(js_code, content_type="application/javascript")
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO PriceSync_exchangerate VALUES('"+insertdexrate.rateDate+"','"+insertdexrate.rateBaseCurrency+"','"+insertdexrate.rateTargetCurrency+"','"+insertdexrate.rateValue+"','"+insertdexrate.rateUpdatedBy+"','"+insertdexrate.rateUpdatedOn+"')")
                cursor.commit()
                #get the data back
                cursor.execute("SELECT * FROM PriceSync_exchangerate ORDER BY rateDate DESC")
                result = cursor.fetchall()
                return render(request, 'ps_blocks/rateUpdateLog.html', {'ExchangeRate':result})
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PriceSync_exchangerate ORDER BY rateDate DESC")
    result = cursor.fetchall()
    return render(request, 'ps_blocks/rateUpdateLog.html', {'ExchangeRate':result})



def costfactors(request):
    return render(request, 'ps_blocks/costfactorspanel.html')

# pages to create
def uploadplist(request):
    if request.method == 'POST':
        if request.POST.get('supplier_name') and request.POST.get('pl_currency'):
            pricelist_resource = pricelistResource()
            dataset = Dataset()
            new_pricelist = request.FILES['my_file']
            imported_data = dataset.load(new_pricelist.read(), format='xlsx')
            supplier_val = request.POST.get('supplier_name')
            currency_val = request.POST.get('pl_currency')
            for data in imported_data:
                value = PriceList(
                    data[0],
                    data[1],
                    data[2],
                    currency_val,
                    supplier_val
                )
                value.save()

    return render(request, 'ps_blocks/uploadpricelist.html')

def viewpricelist(request):
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PriceSync_pricelist")
            # Commit the changes
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

        except Exception as e:
            # Handle any exceptions or errors here
            print(f"Error: {str(e)}")


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PriceSync_pricelist")
    result = cursor.fetchall()
    return render(request, 'ps_blocks/pricelist.html', {'PriceList':result})

def updatecurrencyrates(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def syncinventorydata(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def inventorypricing(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def lcostcalculations(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def integrationsetting(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def BPOreports(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def createaccount(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def usermgt(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def resetpwd(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def errorpage(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def systemaccesslog(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def viewactivitylog(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def audittrailconfigs(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def documentationpanel(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def faqspanel(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def contactsupport(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def releasenotes(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def systemconfigurations(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def securityandpermissions(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def backupandrestore(request):
    return render(request, 'ps_blocks/under_maintenance.html')
