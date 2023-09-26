"""
URL configuration for NashuaXpress project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
   #path('admin/', admin.site.urls),
   path('', views.dashboard, name='dashboard'),
   path('login', views.login, name='login'),
   path('register', views.signup, name='register'),
   path('rateupdatelog', views.rateupdate, name='rateupdatelog'),
   path('costfactorspanel', views.costfactors, name='costfactorspanel'),
   path('uploadpricelist', views.uploadplist, name='uploadpricelist'),
   path('pricelist', views.viewpricelist, name='pricelist'),
   path('rates', views.updatecurrencyrates, name='rates'),
   path('syncinventory', views.syncinventorydata, name='syncinventory'),
   path('inventory', views.inventorypricing, name='inventory'),
   path('calculatecost', views.lcostcalculations, name='calculatecost'),
   path('integrationsettings', views.integrationsetting, name='integrationsettings'),
   path('BPOreporting', views.BPOreports, name='BPOreporting'),
   path('createuser', views.createaccount, name='createuser'),
   path('users', views.usermgt, name='users'),
   path('forgot', views.forgotpassword, name='forgot'),
   path('reset', views.resetpwd, name='reset'),
   path('error', views.errorpage, name='error'),
   path('accesslog', views.systemaccesslog, name='accesslog'),
   path('activitylog', views.viewactivitylog, name='activitylog'),
   path('auditconfigs', views.audittrailconfigs, name='auditconfigs'),
   path('documentation', views.documentationpanel, name='documentation'),
   path('faqs', views.faqspanel, name='faqs'),
   path('support', views.contactsupport, name='support'),
   path('release', views.releasenotes, name='release'),
   path('system', views.systemconfigurations, name='system'),
   path('security', views.securityandpermissions, name='security'),
   path('BackupRestoreCenter', views.backupandrestore, name='HostCenter'),
]
