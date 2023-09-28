from django.shortcuts import render
from django.http import HttpResponse
from tablib import Dataset
from .models import PriceList
from .resources import pricelistResource




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
    return render(request, 'ps_blocks/rateUpdateLog.html')

def costfactors(request):
    return render(request, 'ps_blocks/costfactorspanel.html')

# pages to create
def uploadplist(request):
    if request.method == 'POST':
        pricelist_resource = pricelistResource()
        dataset = Dataset()
        new_pricelist = request.FILES['my_file']
        imported_data = dataset.load(new_pricelist.read(), format='xlsx')
        for data in imported_data:
            value = PriceList(
                data[0],
                data[1],
                data[2]
            )
            value.save()

    return render(request, 'ps_blocks/uploadpricelist.html')

def viewpricelist(request):
    return render(request, 'ps_blocks/under_maintenance.html')

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
