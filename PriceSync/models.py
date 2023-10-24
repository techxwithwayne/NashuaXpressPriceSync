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
    prodID = models.CharField(max_length=40, primary_key=True, null=False, blank=False)
    prodCode = models.CharField(max_length=40, default=0, null=False, blank=False, verbose_name='Product Code', help_text='Enter the product code.')
    prodDesc = models.TextField(blank=True, null=True)
    prodCategory = models.CharField(max_length=255, verbose_name="Product Category")
    prodDOC = models.DateField(verbose_name="Date of Creation")




class ProductCostMapping(models.Model):
    prodID = models.CharField(max_length=40, primary_key=True, null=False, blank=False)
    prodSupplierCode = models.CharField(max_length=40, default=0, null=False, blank=False, verbose_name='Product Supplier Code', help_text='Enter the product supplier code.')
    prodNashuaCode = models.CharField(max_length=40, null=True, blank=True, verbose_name='Product Nashua Code', help_text='Enter the product nashua code.')
    prodDesc = models.TextField(blank=True, null=True)
    prodCategory = models.CharField(max_length=255, verbose_name="Product Category")
    prodSupplierName = models.CharField(max_length=255, verbose_name="Supplier Name", blank=True, null=True)
    prodSupplierCurrency = models.CharField(max_length=3, blank=True, null=True)
    prodCalculationModifier = models.CharField(max_length=50, default="Null", verbose_name="Modify Method on Calculation") 
    prodSupplierCost = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodSupplierCostUSD = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodSupplierLandedCost_USD = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodNashuaSellingPrice_USD = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    prodCalculatedPriceDate = models.DateField(verbose_name="Calculated On", default=date.today)




class ProductCostingFactors(models.Model):
    StockCategory = models.CharField(max_length=255, verbose_name="Product Category")
    SupplierName = models.CharField(max_length=255, verbose_name="Supplier Name", blank=True, null=True)
    CalculationModifier = models.CharField(max_length=255, blank=True, null=True)
    CurrencyCode = models.CharField(max_length=3)
    DutyFactor = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    FreightChargesFactor = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    MarkupFactor = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    UpdatedBy = models.CharField(max_length=100)
    UpdatedOn = models.DateField()



class Suppliers(models.Model):
    SupplierName = models.CharField(max_length=100)
    Contact_person = models.CharField(max_length=100, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Phone_number = models.CharField(max_length=20, blank=True, null=True)
    Address = models.TextField(blank=True, null=True)
    City = models.CharField(max_length=50, blank=True, null=True)
    State = models.CharField(max_length=50, blank=True, null=True)
    Postal_code = models.CharField(max_length=10, blank=True, null=True)
    Country = models.CharField(max_length=50, blank=True, null=True)
    CreatedBy = models.CharField(max_length=100)
    CreatedOn = models.DateField()

    def __str__(self):
        return self.name
    





class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class UserDepartment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(UserDepartment, on_delete=models.SET_NULL, null=True)
    employee_id = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    employee_status = models.CharField(
        max_length=10,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('On Leave', 'On Leave')],
        default='Active'
    )
    date_of_hire = models.DateField(null=True, blank=True)
    account_creation_date = models.DateTimeField(auto_now_add=True)
    profile_picture_url = models.CharField(max_length=255, blank=True, null=True)
    updatedBy = models.CharField(max_length=100)
    updatedOn = models.DateField()

    def __str__(self):
        return self.username





    
