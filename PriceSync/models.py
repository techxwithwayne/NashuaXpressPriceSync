from datetime import date
from django.db import models

# dont forget to run py manage.py makemigrations PriceSync 
# then run py manage.py migrate PriceSync

# Create your models here.
class PriceList(models.Model):
    prodCode = models.CharField(max_length=40, primary_key=True, null=False, blank=False, verbose_name='Product Code', help_text='Enter the product code.')
    prodDesc = models.TextField(blank=True, null=True)
    prodPrice = models.DecimalField(max_digits=18, decimal_places=2)
    prodCurrency = models.CharField(max_length=3, null=True)
    prodSupplier = models.CharField(max_length=255, null=True)

#    def __str__(self):
#        return self.prodCode


from django.db import models

class ExchangeRate(models.Model):
    rateDate = models.DateField()
    rateBaseCurrency = models.CharField(max_length=3)  # ISO 4217 currency code
    rateTargetCurrency = models.CharField(max_length=3)  # ISO 4217 currency code
    rateValue = models.DecimalField(max_digits=18, decimal_places=2)
    rateUpdatedBy = models.CharField(max_length=100)
    rateUpdatedOn = models.DateField()

    def __str__(self):
        return f"{self.rateDate} - {self.rateBaseCurrency}/{self.rateTargetCurrency}: {self.rateValue}"
    



class MasterInventory(models.Model):
    prodCode = models.CharField(max_length=40, primary_key=True, null=False, blank=False, verbose_name='Product Code', help_text='Enter the product code.')
    prodDesc = models.TextField(blank=True, null=True)
    prodCategory = models.CharField(max_length=255, verbose_name="Product Category")
    prodDOC = models.DateField(verbose_name="Date of Creation")




class ProductCostMapping(models.Model):
    prodSupplierCode = models.CharField(max_length=40, primary_key=True, null=False, blank=False, verbose_name='Product Supplier Code', help_text='Enter the product supplier code.')
    prodNashuaCode = models.CharField(max_length=40, null=True, blank=True, verbose_name='Product Nashua Code', help_text='Enter the product nashua code.')
    prodDesc = models.TextField(blank=True, null=True)
    prodCategory = models.CharField(max_length=255, verbose_name="Product Category")
    prodSupplierName = models.CharField(max_length=255, verbose_name="Supplier Name", blank=True, null=True)
    prodSupplierCurrency = models.CharField(max_length=3, blank=True, null=True)
    prodSupplierCost = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodSupplierLandedCost_USD = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodNashuaSellingPrice_USD = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodCalculatedPriceDate = models.DateField(verbose_name="Calculated On", default=date.today)




    
